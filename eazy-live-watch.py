#!/usr/bin/env python3
"""Monitor de arquivos do Easy: full.c -> fila privada -> SQLite -> refresh FZF."""
from __future__ import annotations

import argparse
import base64
import fcntl
import glob
import os
import re
import signal
import socket
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

STOP = False


def log(state_dir: Path, message: str) -> None:
    try:
        state_dir.mkdir(parents=True, exist_ok=True)
        with (state_dir / "watch.log").open("a", encoding="utf-8", errors="replace") as fh:
            fh.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {message}\n")
    except OSError:
        pass


def atomic_write(path: Path, data: bytes, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise


def ensure_private_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    st = path.stat()
    if st.st_uid != os.getuid() or not path.is_dir():
        raise RuntimeError(f"Diretório da fila não pertence ao usuário atual: {path}")
    os.chmod(path, 0o700)


def source_path(script_path: Path) -> Path:
    candidates = [script_path.parent / "full.c", Path("/usr/lib/eazy/full.c")]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise RuntimeError("full.c não foi encontrado ao lado de eazy-live-watch.py nem em /usr/lib/eazy")


def build_monitor(script_path: Path, state_dir: Path) -> Path:
    src = source_path(script_path)
    binary = state_dir / "full"
    try:
        if binary.is_file() and binary.stat().st_mtime_ns >= src.stat().st_mtime_ns:
            return binary
    except OSError:
        pass
    compiler = os.environ.get("CC", "cc")
    if not shutil_which(compiler):
        raise RuntimeError("Compilador C (cc/gcc) não encontrado; instale um compilador para ativar o monitor")
    temp = state_dir / f"full.build.{os.getpid()}"
    command = [compiler, "-std=c11", "-O2", "-Wall", "-Wextra", "-D_FILE_OFFSET_BITS=64", str(src), "-o", str(temp)]
    proc = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    if proc.returncode != 0:
        try:
            temp.unlink()
        except OSError:
            pass
        detail = (proc.stderr or proc.stdout or "falha de compilação").strip()
        raise RuntimeError(f"Não foi possível compilar o monitor C: {detail[-1800:]}")
    os.chmod(temp, 0o700)
    os.replace(temp, binary)
    return binary


def shutil_which(command: str) -> str | None:
    # Evita importar uma camada de dependências para uma operação simples.
    from shutil import which
    return which(command)


def read_pid(state_dir: Path) -> int | None:
    try:
        return int((state_dir / "pid").read_text(encoding="ascii").strip())
    except (OSError, ValueError):
        return None


def process_is_ours(pid: int, script_path: Path) -> bool:
    if pid <= 1:
        return False
    try:
        raw = Path(f"/proc/{pid}/cmdline").read_bytes()
        return os.fsencode(str(script_path)) in raw and b"_run" in raw
    except OSError:
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False


def stop_orphan_monitor_binary(state_dir: Path) -> None:
    """Stop only full processes launched from this root's private state dir."""
    binary = (state_dir / "full").resolve()
    owned: list[int] = []
    proc_root = Path("/proc")
    try:
        entries = list(proc_root.iterdir())
    except OSError:
        return
    for entry in entries:
        if not entry.name.isdigit() or int(entry.name) <= 1:
            continue
        try:
            argv = (entry / "cmdline").read_bytes().split(b"\0")
            if not argv or not argv[0] or Path(os.fsdecode(argv[0])).resolve() != binary:
                continue
            if b"/start" not in argv and b"/start" not in (b"\0".join(argv)):
                continue
            owned.append(int(entry.name))
        except (OSError, ValueError):
            continue
    for pid in owned:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    deadline = time.monotonic() + 2.0
    while time.monotonic() < deadline:
        alive = []
        for pid in owned:
            try:
                raw = Path(f"/proc/{pid}/cmdline").read_bytes().split(b"\0")
                if raw and raw[0] and Path(os.fsdecode(raw[0])).resolve() == binary:
                    alive.append(pid)
            except (OSError, ValueError):
                pass
        if not alive:
            return
        time.sleep(0.05)
    for pid in owned:
        try:
            raw = Path(f"/proc/{pid}/cmdline").read_bytes().split(b"\0")
            if raw and raw[0] and Path(os.fsdecode(raw[0])).resolve() == binary:
                os.kill(pid, signal.SIGKILL)
        except (OSError, ValueError):
            pass


def stop_persisted_windows_watcher(state_dir: Path) -> None:
    """Stop a recorded Windows watcher only if its PID and start-time still match."""
    try:
        fields = (state_dir / "windows-process").read_text(encoding="ascii").split()
        pid, start_ticks = int(fields[0]), int(fields[1])
    except (OSError, ValueError, IndexError):
        return
    if pid <= 1 or start_ticks <= 0:
        return
    powershell = shutil_which("powershell.exe") or shutil_which("pwsh.exe")
    if powershell:
        command = (
            f"$p=Get-Process -Id {pid} -ErrorAction SilentlyContinue; "
            f"if ($p -and $p.StartTime.ToUniversalTime().Ticks -eq {start_ticks}) "
            "{$p.Kill()}"
        )
        encoded = base64.b64encode(command.encode("utf-16le")).decode("ascii")
        try:
            subprocess.run([powershell, "-NoLogo", "-NoProfile", "-NonInteractive",
                            "-EncodedCommand", encoded], stdin=subprocess.DEVNULL,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           timeout=4, check=False)
        except (OSError, subprocess.SubprocessError):
            pass
    try:
        (state_dir / "windows-process").unlink()
    except OSError:
        pass


def status(state_dir: Path, script_path: Path) -> tuple[bool, str]:
    pid = read_pid(state_dir)
    if pid and process_is_ours(pid, script_path):
        try:
            root = (state_dir / "root").read_text(encoding="utf-8", errors="surrogateescape").rstrip("\n")
        except OSError:
            root = "raiz não registrada"
        return True, root
    return False, ""


def control_lock(state_dir: Path):
    state_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(state_dir, 0o700)
    fh = (state_dir / "control.lock").open("a+b")
    fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
    return fh


def select_queue(state_dir: Path) -> Path:
    candidate = Path(f"/dev/shm/eazy-livewatch-{os.getuid()}")
    try:
        ensure_private_dir(candidate)
        return candidate
    except OSError:
        fallback = state_dir / "events"
        ensure_private_dir(fallback)
        return fallback


def command_start(args: argparse.Namespace, script_path: Path) -> int:
    state_dir = Path(args.state_dir).expanduser().resolve()
    root = Path(args.root).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise RuntimeError(f"A raiz escolhida não é uma pasta: {root}")
    indexer = Path(args.indexer).expanduser().resolve(strict=True)
    database = Path(args.db).expanduser().resolve()
    sessions_dir = Path(args.sessions_dir).expanduser().resolve()
    exclude = Path(args.exclude).expanduser().resolve() if args.exclude else Path()
    queue = Path(args.queue_dir).expanduser().resolve() if args.queue_dir else select_queue(state_dir)
    ensure_private_dir(state_dir)
    ensure_private_dir(queue)
    ensure_private_dir(sessions_dir)
    with control_lock(state_dir):
        active, active_root = status(state_dir, script_path)
        if active:
            if active_root == str(root):
                print(f"Monitor já ativo para: {root}")
                return 0
            raise RuntimeError(f"Já existe um monitor ativo para {active_root}; pare-o pelo F9 antes de escolher outra raiz")
        binary = build_monitor(script_path, state_dir)
        try:
            (state_dir / "backend-ready").unlink()
        except OSError:
            pass
        log_path = state_dir / "watch.log"
        with log_path.open("ab", buffering=0) as log_fh:
            proc = subprocess.Popen(
                [sys.executable, str(script_path), "_run", "--state-dir", str(state_dir),
                 "--root", str(root), "--indexer", str(indexer), "--db", str(database),
                 "--exclude", str(exclude) if str(exclude) != "." else "",
                 "--queue-dir", str(queue), "--sessions-dir", str(sessions_dir),
                 "--binary", str(binary), "--hidden" if args.hidden else "--no-hidden"],
                stdin=subprocess.DEVNULL, stdout=log_fh, stderr=log_fh,
                start_new_session=True, close_fds=True,
            )
        atomic_write(state_dir / "pid", f"{proc.pid}\n".encode("ascii"))
        atomic_write(state_dir / "root", (str(root) + "\n").encode("utf-8", "surrogateescape"))
    deadline = time.monotonic() + (15.0 if is_wsl_windows_drive(str(root)) else 4.0)
    while time.monotonic() < deadline:
        if process_is_ours(proc.pid, script_path):
            time.sleep(0.2)
            ready = not is_wsl_windows_drive(str(root)) or (state_dir / "backend-ready").is_file()
            if proc.poll() is None and ready:
                print(f"Monitor recursivo iniciado para: {root}")
                return 0
        if proc.poll() is not None:
            break
        time.sleep(0.05)
    raise RuntimeError(f"O monitor não permaneceu ativo. Consulte {state_dir / 'watch.log'}")


def command_stop(args: argparse.Namespace, script_path: Path) -> int:
    state_dir = Path(args.state_dir).expanduser().resolve()
    with control_lock(state_dir):
        pid = read_pid(state_dir)
        if not pid or not process_is_ours(pid, script_path):
            stop_persisted_windows_watcher(state_dir)
            stop_orphan_monitor_binary(state_dir)
            print("Monitor já está parado")
            for name in ("pid", "root", "backend-ready"):
                try:
                    (state_dir / name).unlink()
                except OSError:
                    pass
            return 0
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    deadline = time.monotonic() + 20.0
    while time.monotonic() < deadline and process_is_ours(pid, script_path):
        time.sleep(0.1)
    if process_is_ours(pid, script_path):
        # The controller may be waiting for an indexer operation. Stop only
        # this instance's owned backends before the final controller fallback.
        stop_persisted_windows_watcher(state_dir)
        stop_orphan_monitor_binary(state_dir)
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline and process_is_ours(pid, script_path):
            time.sleep(0.1)
    if process_is_ours(pid, script_path):
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    stop_persisted_windows_watcher(state_dir)
    stop_orphan_monitor_binary(state_dir)
    for name in ("pid", "root", "backend-ready"):
        try:
            (state_dir / name).unlink()
        except OSError:
            pass
    print("Monitor parado")
    return 0


def inside(path: str, root: str) -> bool:
    try:
        return os.path.commonpath((os.path.realpath(path), os.path.realpath(root))) == os.path.realpath(root)
    except (OSError, ValueError):
        return False


def run_indexer(indexer: Path, db: Path, operation: str, path: str, exclude: str, state_dir: Path) -> bool:
    cmd = [sys.executable, str(indexer), "--db", str(db), operation, path]
    if exclude:
        cmd.extend(("--exclude-path", exclude))
    proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                          text=True, errors="replace", check=False)
    if proc.returncode != 0:
        detail = (proc.stderr or f"exit={proc.returncode}").strip().replace("\n", " ")
        log(state_dir, f"indexador falhou: {operation} {path}: {detail[:500]}")
        return False
    return True


def read_ticket(path: Path) -> tuple[str, str] | None:
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    if len(raw) < 3 or raw[1:2] != b"\0" or not raw.endswith(b"\0"):
        return None
    op = raw[:1].decode("ascii", "replace")
    item = os.fsdecode(raw[2:-1])
    if not item:
        return None
    return op, item


def load_session(path: Path) -> tuple[int, str, Path] | None:
    try:
        fields = path.read_bytes().split(b"\0")
        if len(fields) < 4:
            return None
        port = int(fields[0].decode("ascii", "strict"))
        current = os.fsdecode(fields[1])
        refresh = Path(os.fsdecode(fields[2]))
        if not current or not str(refresh):
            return None
        return port, current, refresh
    except (OSError, ValueError, UnicodeError):
        return None


def notify_sessions(sessions_dir: Path, parents: set[str], root_scan: bool,
                    root: str, state_dir: Path) -> None:
    try:
        sessions = list(sessions_dir.glob("*.session"))
    except OSError:
        return
    token = str(time.time_ns()).encode("ascii") + b"\n"
    for session in sessions:
        data = load_session(session)
        if not data:
            continue
        port, current, refresh = data
        current_real = os.path.realpath(current)
        changed_parents = {os.path.realpath(p) for p in parents}
        affected = any(current_real == parent or inside(parent, current_real)
                       for parent in changed_parents)
        if root_scan and inside(current_real, root):
            affected = True
        if not affected:
            continue
        try:
            atomic_write(refresh, token)
        except OSError as exc:
            log(state_dir, f"não foi possível marcar refresh {refresh}: {exc}")
            continue
        if port <= 0 or port > 65535:
            continue
        body = b"reload(eazy_lista_filtrada_live '{q}')"
        request = urllib.request.Request(
            f"http://127.0.0.1:{port}/", data=body,
            headers={"Content-Type": "text/plain"}, method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=0.35) as response:
                response.read(128)
        except (OSError, urllib.error.URLError, TimeoutError):
            # O marcador segue válido; o próximo reload por digitação também o consome.
            pass


def drain_events(queue: Path, state_dir: Path) -> list[tuple[Path, str, str]]:
    found: list[tuple[Path, str, str]] = []
    try:
        names = sorted(queue.glob("*.evt"))
    except OSError:
        return found
    for ticket in names:
        record = read_ticket(ticket)
        if record:
            found.append((ticket, record[0], record[1]))
        else:
            log(state_dir, f"ticket inválido; descartado: {ticket.name}")
            try:
                ticket.unlink()
            except OSError:
                pass
    return found


def process_batch(events: list[tuple[Path, str, str]], root: str, indexer: Path,
                  db: Path, exclude: str, sessions: Path, state_dir: Path) -> bool:
    parents: set[str] = set()
    new_dirs: set[str] = set()
    windows_created_files: set[str] = set()
    full_rescan = False
    for _ticket, op, item in events:
        if op == "!":
            full_rescan = True
            continue
        parent = os.path.dirname(item.rstrip(os.sep)) or os.sep
        if inside(parent, root):
            parents.add(parent)
        if op == "C" and inside(item, root):
            windows_created_files.add(item)
        if op == "D" and os.path.isdir(item) and inside(item, root):
            new_dirs.add(item)
        if op == "R" and os.path.isdir(item) and inside(item, root):
            # O sinal Move/Delete Self aponta para uma árvore que continua no local.
            new_dirs.add(item)
    ok = True
    if full_rescan:
        ok = run_indexer(indexer, db, "--scan-tree", root, exclude, state_dir) and ok
    for parent in sorted(parents):
        if os.path.isdir(parent):
            ok = run_indexer(indexer, db, "--sync-dir", parent, exclude, state_dir) and ok
    # FileSystemWatcher pode notificar Created antes de DrvFs expor a entrada
    # numa enumeração Linux. Só para tickets C do watcher Windows: confirmar a
    # linha ativa e, se necessário, invalidar a assinatura e repetir a pasta.
    for item in sorted(windows_created_files):
        if not inside(item, root):
            continue
        parent = os.path.dirname(item.rstrip(os.sep)) or os.sep
        indexed = False
        for attempt in range(3):
            if not os.path.isfile(item):
                time.sleep(0.25)
                continue
            try:
                with sqlite3.connect(db, timeout=10) as con:
                    indexed = con.execute(
                        "SELECT 1 FROM files WHERE path=? AND deleted=0 LIMIT 1", (item,)
                    ).fetchone() is not None
            except sqlite3.Error as exc:
                log(state_dir, f"não foi possível confirmar criação no SQLite {item}: {exc}")
                ok = False
                break
            if indexed:
                break
            if attempt:
                time.sleep(0.25)
            try:
                with sqlite3.connect(db, timeout=10) as con:
                    con.execute("DELETE FROM directory_signatures WHERE path=?", (parent,))
                    con.commit()
            except sqlite3.Error as exc:
                log(state_dir, f"não foi possível invalidar assinatura de {parent}: {exc}")
                ok = False
                break
            if not run_indexer(indexer, db, "--sync-dir", parent, exclude, state_dir):
                ok = False
                break
        if not indexed and os.path.isfile(item):
            log(state_dir, f"criação Windows ainda não visível no SQLite após nova sincronização: {item}")
            ok = False
    # Um novo/movido diretório traz potencialmente uma árvore ainda não indexada.
    roots: list[str] = []
    for candidate in sorted(new_dirs, key=lambda p: (p.count(os.sep), p)):
        if not any(inside(candidate, prior) for prior in roots):
            roots.append(candidate)
    for new_root in roots:
        if os.path.isdir(new_root):
            ok = run_indexer(indexer, db, "--scan-tree", new_root, exclude, state_dir) and ok
    if events and ok:
        notify_sessions(sessions, parents, full_rescan, root, state_dir)
        for ticket, _op, _item in events:
            try:
                ticket.unlink()
            except OSError as exc:
                log(state_dir, f"ticket sincronizado, mas não removido {ticket.name}: {exc}")
    elif events:
        log(state_dir, f"{len(events)} ticket(s) mantido(s) para nova tentativa após falha SQLite")
    return ok


def is_wsl_windows_drive(root: str) -> bool:
    return re.match(r"^/mnt/[a-z](?:/|$)", os.path.normpath(root), re.IGNORECASE) is not None


def stop_windows_watcher(handle: dict | None, state_dir: Path) -> None:
    if not handle:
        return
    proc = handle.get("proc")
    windows_pid = handle.get("windows_pid")
    powershell = handle.get("powershell")
    if windows_pid and powershell:
        command = f"Stop-Process -Id {int(windows_pid)} -Force -ErrorAction SilentlyContinue"
        encoded = base64.b64encode(command.encode("utf-16le")).decode("ascii")
        try:
            subprocess.run([powershell, "-NoLogo", "-NoProfile", "-NonInteractive",
                            "-EncodedCommand", encoded], stdin=subprocess.DEVNULL,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           timeout=3, check=False)
        except (OSError, subprocess.SubprocessError):
            pass
    if proc is not None and proc.poll() is None:
        try:
            proc.terminate()
            proc.wait(timeout=2)
        except (OSError, subprocess.TimeoutExpired):
            try:
                proc.kill()
                proc.wait(timeout=2)
            except (OSError, subprocess.SubprocessError):
                log(state_dir, "não foi possível encerrar o processo FileSystemWatcher")
    if proc is not None and proc.stdout is not None:
        try:
            proc.stdout.close()
        except OSError:
            pass
    try:
        (state_dir / "windows-process").unlink()
    except OSError:
        pass
    reader = handle.get("reader")
    if reader is not None and reader.is_alive():
        reader.join(timeout=0.5)


def start_windows_watcher(root: str, queue: Path, state_dir: Path,
                          hidden: bool, exclude: str, log_fh) -> dict | None:
    if not is_wsl_windows_drive(root):
        return None
    powershell = shutil_which("powershell.exe") or shutil_which("pwsh.exe")
    wslpath = shutil_which("wslpath")
    if not powershell or not wslpath:
        raise RuntimeError("/mnt/<unidade> no WSL2 exige powershell.exe/pwsh.exe e wslpath para receber eventos do Windows")
    converted = subprocess.run([wslpath, "-w", root], stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, timeout=5, check=False)
    if converted.returncode != 0 or not converted.stdout.strip():
        detail = converted.stderr.strip() or "wslpath não converteu a raiz"
        raise RuntimeError(f"Não foi possível mapear a raiz WSL para o Windows: {detail}")
    windows_root = converted.stdout.strip()
    root_b64 = base64.b64encode(windows_root.encode("utf-8")).decode("ascii")
    csharp = r'''using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Threading;
public static class EazyNativeWatcher {
    private static readonly object Gate = new object();
    private static string Root;
    private static string Prefix;
    private static void Emit(char op, string fullPath) {
        string relative = fullPath;
        if (String.Equals(fullPath, Root, StringComparison.OrdinalIgnoreCase)) relative = ".";
        else if (fullPath.StartsWith(Prefix, StringComparison.OrdinalIgnoreCase)) relative = fullPath.Substring(Prefix.Length);
        string encoded = Convert.ToBase64String(Encoding.UTF8.GetBytes(relative));
        lock (Gate) { Console.WriteLine("EV|" + op + "|" + encoded); Console.Out.Flush(); }
    }
    public static void Run(string root) {
        Root = root;
        Prefix = root.EndsWith("\\", StringComparison.Ordinal) ? root : root + "\\";
        FileSystemWatcher watcher = new FileSystemWatcher(root);
        watcher.IncludeSubdirectories = true;
        watcher.NotifyFilter = NotifyFilters.FileName | NotifyFilters.DirectoryName | NotifyFilters.LastWrite | NotifyFilters.Size | NotifyFilters.CreationTime | NotifyFilters.Attributes;
        watcher.InternalBufferSize = 65536;
        watcher.Created += delegate(object s, FileSystemEventArgs e) { Emit(Directory.Exists(e.FullPath) ? 'D' : 'C', e.FullPath); };
        watcher.Changed += delegate(object s, FileSystemEventArgs e) { Emit('U', e.FullPath); };
        watcher.Deleted += delegate(object s, FileSystemEventArgs e) { Emit('X', e.FullPath); };
        watcher.Renamed += delegate(object s, RenamedEventArgs e) { Emit('X', e.OldFullPath); Emit(Directory.Exists(e.FullPath) ? 'D' : 'U', e.FullPath); };
        watcher.Error += delegate(object s, ErrorEventArgs e) { Emit('!', Root); };
        watcher.EnableRaisingEvents = true;
        Console.WriteLine("READY|" + Process.GetCurrentProcess().Id + "|" + Process.GetCurrentProcess().StartTime.ToUniversalTime().Ticks);
        Console.Out.Flush();
        Thread.Sleep(Timeout.Infinite);
    }
}'''
    script = (
        "$ErrorActionPreference='Stop'\n"
        "$utf8=New-Object System.Text.UTF8Encoding $false\n"
        "[Console]::OutputEncoding=$utf8\n"
        f"$root=[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('{root_b64}'))\n"
        "$source=@'\n" + csharp + "\n'@\n"
        "Add-Type -TypeDefinition $source -Language CSharp\n"
        "[EazyNativeWatcher]::Run($root)\n"
    )
    encoded_script = base64.b64encode(script.encode("utf-16le")).decode("ascii")
    proc = subprocess.Popen([powershell, "-NoLogo", "-NoProfile", "-NonInteractive",
                             "-ExecutionPolicy", "Bypass", "-EncodedCommand", encoded_script],
                           stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                           stderr=log_fh, bufsize=0, close_fds=True)
    ready = threading.Event()
    reader_done = threading.Event()
    details: dict[str, int] = {}

    def queue_event(op: str, payload: bytes) -> None:
        try:
            if op == "!":
                item = root
            else:
                relative = os.fsdecode(base64.b64decode(payload, validate=True)).replace("\\", os.sep)
                item = root if relative in ("", ".") else os.path.normpath(os.path.join(root, relative))
                if not inside(item, root):
                    return
                if not hidden and any(part.startswith(".") for part in relative.split(os.sep)):
                    return
                if exclude and inside(item, exclude):
                    return
            name = f"win_{os.getpid()}_{time.time_ns()}_{threading.get_ident()}.evt"
            atomic_write(queue / name, op.encode("ascii") + b"\0" + os.fsencode(item) + b"\0")
        except (OSError, ValueError, base64.binascii.Error) as exc:
            log(state_dir, f"evento FileSystemWatcher inválido: {exc}")

    def read_output() -> None:
        try:
            assert proc.stdout is not None
            for raw in proc.stdout:
                line = raw.decode("ascii", "replace").strip()
                if line.startswith("READY|"):
                    try:
                        fields = line.split("|")
                        details["windows_pid"] = int(fields[1])
                        details["windows_start_ticks"] = int(fields[2])
                        ready.set()
                    except ValueError:
                        pass
                elif line.startswith("EV|"):
                    fields = line.split("|", 2)
                    if len(fields) == 3 and len(fields[1]) == 1:
                        queue_event(fields[1], fields[2].encode("ascii"))
        except (OSError, AssertionError) as exc:
            log(state_dir, f"leitura do FileSystemWatcher terminou: {exc}")
        finally:
            reader_done.set()

    reader = threading.Thread(target=read_output, name="eazy-windows-watch", daemon=True)
    handle = {"proc": proc, "powershell": powershell, "reader": reader,
              "reader_done": reader_done}
    reader.start()
    if not ready.wait(timeout=8) or proc.poll() is not None or reader_done.is_set() or "windows_pid" not in details:
        handle.update(details)
        stop_windows_watcher(handle, state_dir)
        raise RuntimeError(f"FileSystemWatcher do Windows não iniciou para {root}; consulte {state_dir / 'watch.log'}")
    handle.update(details)
    if "windows_pid" in details and "windows_start_ticks" in details:
        atomic_write(state_dir / "windows-process",
                     f"{details['windows_pid']} {details['windows_start_ticks']}\n".encode("ascii"))
    log(state_dir, f"FileSystemWatcher ativo root={root} windows_pid={details['windows_pid']}")
    return handle


def run_daemon(args: argparse.Namespace, script_path: Path) -> int:
    global STOP
    state_dir = Path(args.state_dir).resolve()
    root = str(Path(args.root).resolve(strict=True))
    indexer = Path(args.indexer).resolve(strict=True)
    db = Path(args.db).resolve()
    exclude = str(Path(args.exclude).resolve()) if args.exclude else ""
    queue = Path(args.queue_dir).resolve()
    sessions = Path(args.sessions_dir).resolve()
    binary = Path(args.binary).resolve()
    ensure_private_dir(state_dir)
    ensure_private_dir(queue)
    ensure_private_dir(sessions)

    def handle_signal(_sig, _frame):
        STOP = True
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    atomic_write(state_dir / "pid", f"{os.getpid()}\n".encode("ascii"))
    atomic_write(state_dir / "root", (root + "\n").encode("utf-8", "surrogateescape"))
    with (state_dir / "watch.log").open("ab", buffering=0) as log_fh:
        monitor = None
        windows_watcher = None
        try:
            c_args = [str(binary), root, "/s", "/start", "--queue", str(queue)]
            if args.hidden:
                c_args.append("/h")
            if exclude:
                c_args.extend(("--exclude", exclude))
            monitor = subprocess.Popen(c_args, stdin=subprocess.DEVNULL,
                                       stdout=subprocess.DEVNULL, stderr=log_fh,
                                       start_new_session=True, close_fds=True)
            windows_watcher = start_windows_watcher(root, queue, state_dir,
                                                     args.hidden, exclude, log_fh)
            if windows_watcher is not None:
                atomic_write(state_dir / "backend-ready", b"windows\n")
            if monitor is not None:
                log(state_dir, f"full iniciou root={root} pid={monitor.pid} modo=recursivo tickets=on ocultos={args.hidden}")
            if windows_watcher is not None:
                log(state_dir, f"FileSystemWatcher complementar ativo root={root} windows_pid={windows_watcher['windows_pid']}")
            # Conferência rasa inicial da raiz, sem varrer toda a árvore. O F9
            # pode ser usado em uma raiz já indexada; árvores novas e perdas
            # sinalizadas pelos backends são percorridas sob demanda.
            run_indexer(indexer, db, "--sync-dir", root, exclude, state_dir)
            while not STOP:
                if monitor is not None and monitor.poll() is not None:
                    log(state_dir, f"full terminou inesperadamente com código {monitor.returncode}")
                    break
                if windows_watcher is not None and windows_watcher["reader_done"].is_set():
                    log(state_dir, "FileSystemWatcher do Windows terminou inesperadamente")
                    break
                first = drain_events(queue, state_dir)
                if not first:
                    time.sleep(0.08)
                    continue
                # Agrupa bursts de cópia/movimentação em uma sincronização por pai.
                time.sleep(0.12)
                first.extend(drain_events(queue, state_dir))
                # Tickets que ainda estão na fila por falha anterior podem ter
                # aparecido em ambas as leituras; deduplicar antes da transação.
                first = list({str(ticket): (ticket, op, item) for ticket, op, item in first}.values())
                if not process_batch(first, root, indexer, db, exclude, sessions, state_dir):
                    time.sleep(1.0)
            # Processa o que já foi gravado antes de encerrar o monitor.
            stop_windows_watcher(windows_watcher, state_dir)
            windows_watcher = None
            tail = drain_events(queue, state_dir)
            if tail:
                process_batch(tail, root, indexer, db, exclude, sessions, state_dir)
        finally:
            stop_windows_watcher(windows_watcher, state_dir)
            if monitor is not None and monitor.poll() is None:
                monitor.terminate()
                try:
                    monitor.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    monitor.kill()
                    monitor.wait(timeout=2)
            try:
                (state_dir / "pid").unlink()
                (state_dir / "root").unlink()
                (state_dir / "backend-ready").unlink()
            except OSError:
                pass
            log(state_dir, "monitor parado")
    return 0


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Controla o monitor recursivo do Easy")
    sub = ap.add_subparsers(dest="command", required=True)
    for cmd in ("start", "status", "stop"):
        item = sub.add_parser(cmd)
        item.add_argument("--state-dir", required=True)
    start = sub.choices["start"]
    start.add_argument("--root", required=True)
    start.add_argument("--indexer", required=True)
    start.add_argument("--db", required=True)
    start.add_argument("--exclude", default="")
    start.add_argument("--sessions-dir", required=True)
    start.add_argument("--queue-dir", default="")
    start.add_argument("--hidden", action="store_true")
    run = sub.add_parser("_run")
    run.add_argument("--state-dir", required=True)
    run.add_argument("--root", required=True)
    run.add_argument("--indexer", required=True)
    run.add_argument("--db", required=True)
    run.add_argument("--exclude", default="")
    run.add_argument("--queue-dir", required=True)
    run.add_argument("--sessions-dir", required=True)
    run.add_argument("--binary", required=True)
    run.add_argument("--hidden", dest="hidden", action="store_true")
    run.add_argument("--no-hidden", dest="hidden", action="store_false")
    run.set_defaults(hidden=False)
    return ap


def main() -> int:
    args = parser().parse_args()
    script_path = Path(__file__).resolve()
    state_dir = Path(args.state_dir).expanduser().resolve()
    try:
        if args.command == "status":
            active, root = status(state_dir, script_path)
            if active:
                print(f"ATIVO|{root}")
                return 0
            print("DESLIGADO")
            return 1
        if args.command == "start":
            return command_start(args, script_path)
        if args.command == "stop":
            return command_stop(args, script_path)
        if args.command == "_run":
            return run_daemon(args, script_path)
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"eazy-live-watch: {exc}", file=sys.stderr)
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

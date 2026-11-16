#!/usr/bin/env python3
"""Persistent incremental file index for eazy.

The shell UI feeds paths separated by NUL on stdin.  The index stores cheap
filesystem identity/signature fields and media metadata.  CRC32 is internal
validation data only; it is never a user-facing sort key.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sqlite3
import stat
import subprocess
import sys
import time
import zlib
from pathlib import Path

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
CREATE TABLE IF NOT EXISTS files (
    path TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    parent TEXT NOT NULL,
    extension TEXT NOT NULL DEFAULT '',
    kind TEXT NOT NULL DEFAULT 'other',
    mime TEXT NOT NULL DEFAULT '',
    size INTEGER NOT NULL DEFAULT 0,
    mtime_ns INTEGER NOT NULL DEFAULT 0,
    ctime_ns INTEGER NOT NULL DEFAULT 0,
    device INTEGER NOT NULL DEFAULT 0,
    inode INTEGER NOT NULL DEFAULT 0,
    crc32 TEXT NOT NULL DEFAULT '',
    duration_ms INTEGER,
    width INTEGER,
    height INTEGER,
    video_codec TEXT NOT NULL DEFAULT '',
    audio_codec TEXT NOT NULL DEFAULT '',
    bitrate INTEGER,
    indexed_at INTEGER NOT NULL DEFAULT 0,
    deleted INTEGER NOT NULL DEFAULT 0,
    deleted_at INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_files_name ON files(name COLLATE NOCASE);
CREATE INDEX IF NOT EXISTS idx_files_parent ON files(parent);
CREATE INDEX IF NOT EXISTS idx_files_size ON files(size);
CREATE INDEX IF NOT EXISTS idx_files_mtime ON files(mtime_ns);
CREATE INDEX IF NOT EXISTS idx_files_duration ON files(duration_ms);
CREATE INDEX IF NOT EXISTS idx_files_extension ON files(extension);
CREATE TABLE IF NOT EXISTS history_items (
    id INTEGER PRIMARY KEY,
    path TEXT NOT NULL UNIQUE,
    position INTEGER NOT NULL DEFAULT 0,
    played_at INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_history_position ON history_items(position);
"""

VIDEO = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".wmv", ".flv", ".m4v", ".mpg", ".mpeg", ".ts"}
AUDIO = {".mp3", ".m4a", ".wav", ".flac", ".ogg", ".opus", ".aac", ".wma"}
IMAGE = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tif", ".tiff", ".svg"}
ARCHIVE = {".zip", ".tar", ".gz", ".bz2", ".xz", ".rar", ".7z"}


def kind_for(ext: str) -> str:
    if ext in VIDEO:
        return "video"
    if ext in AUDIO:
        return "audio"
    if ext in IMAGE:
        return "image"
    if ext in ARCHIVE:
        return "archive"
    return "other"


def db_open(path: str) -> sqlite3.Connection:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=30)
    db.executescript(SCHEMA)
    # Migração silenciosa de bancos criados antes da marca de exclusão.
    cols = {row[1] for row in db.execute("PRAGMA table_info(files)")}
    if "deleted" not in cols:
        db.execute("ALTER TABLE files ADD COLUMN deleted INTEGER NOT NULL DEFAULT 0")
    if "deleted_at" not in cols:
        db.execute("ALTER TABLE files ADD COLUMN deleted_at INTEGER NOT NULL DEFAULT 0")
    db.commit()
    return db


def crc32_file(path: str) -> str:
    value = 0
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            value = zlib.crc32(block, value)
    return f"{value & 0xffffffff:08x}"


def media_probe(path: str):
    try:
        proc = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_format", "-show_streams", "--", path],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, timeout=20, check=False,
        )
        data = json.loads(proc.stdout or "{}")
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None
    fmt = data.get("format") or {}
    streams = data.get("streams") or []
    video = next((s for s in streams if s.get("codec_type") == "video"), {})
    audio = next((s for s in streams if s.get("codec_type") == "audio"), {})
    duration = fmt.get("duration")
    try:
        duration_ms = round(float(duration) * 1000) if duration not in (None, "N/A") else None
    except (TypeError, ValueError):
        duration_ms = None
    def integer(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
    return {
        "duration_ms": duration_ms,
        "width": integer(video.get("width")),
        "height": integer(video.get("height")),
        "video_codec": str(video.get("codec_name") or ""),
        "audio_codec": str(audio.get("codec_name") or ""),
        "bitrate": integer(fmt.get("bit_rate")),
    }


def row_for(path: str, old):
    st = os.stat(path, follow_symlinks=False)
    name = os.path.basename(path)
    parent = os.path.dirname(path)
    ext = os.path.splitext(name)[1].lower()
    if stat.S_ISDIR(st.st_mode):
        return {
            "path": path, "name": name, "parent": parent, "extension": "",
            "kind": "directory", "mime": "inode/directory", "size": st.st_size,
            "mtime_ns": st.st_mtime_ns, "ctime_ns": st.st_ctime_ns,
            "device": st.st_dev, "inode": st.st_ino, "crc32": "",
            "duration_ms": None, "width": None, "height": None,
            "video_codec": "", "audio_codec": "", "bitrate": None,
            "indexed_at": int(time.time()), "deleted": 0, "deleted_at": 0,
        }
    kind = kind_for(ext)
    # Assinatura rápida: não abre nem lê o conteúdo do arquivo.
    # Tamanho + mtime_ns são a regra principal; dispositivo/inode protegem
    # contra troca do arquivo mantendo o mesmo nome.
    signature = (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns)
    old_signature = None
    if old:
        old_signature = (old["device"], old["inode"], old["size"], old["mtime_ns"])
    changed = old is None or signature != old_signature
    if not changed:
        return None
    mime = mimetypes.guess_type(name, strict=False)[0] or ""
    # CRC não é calculado na indexação: isso exigiria ler o arquivo inteiro.
    # A validação forte ficará restrita aos candidatos da pesquisa de duplicados.
    crc = ""
    crc_unreadable = False
    media = media_probe(path) if kind in ("video", "audio") else {}
    return {
        "path": path, "name": name, "parent": parent, "extension": ext,
        "kind": kind, "mime": mime, "size": st.st_size,
        "mtime_ns": st.st_mtime_ns, "ctime_ns": st.st_ctime_ns,
        "device": st.st_dev, "inode": st.st_ino, "crc32": crc,
        **(media or {"duration_ms": None, "width": None, "height": None,
                     "video_codec": "", "audio_codec": "", "bitrate": None}),
        "indexed_at": int(time.time()),
        "deleted": 0,
        "deleted_at": 0,
        "_crc_unreadable": crc_unreadable,
    }


def scan(db: sqlite3.Connection, paths):
    seen = set()
    changed = 0
    removed = 0
    select = db.execute
    upsert = """
    INSERT INTO files(path,name,parent,extension,kind,mime,size,mtime_ns,ctime_ns,device,inode,crc32,
                      duration_ms,width,height,video_codec,audio_codec,bitrate,indexed_at,deleted,deleted_at)
    VALUES(:path,:name,:parent,:extension,:kind,:mime,:size,:mtime_ns,:ctime_ns,:device,:inode,:crc32,
           :duration_ms,:width,:height,:video_codec,:audio_codec,:bitrate,:indexed_at,:deleted,:deleted_at)
    ON CONFLICT(path) DO UPDATE SET
      name=excluded.name,parent=excluded.parent,extension=excluded.extension,kind=excluded.kind,
      mime=excluded.mime,size=excluded.size,mtime_ns=excluded.mtime_ns,ctime_ns=excluded.ctime_ns,
      device=excluded.device,inode=excluded.inode,crc32=excluded.crc32,duration_ms=excluded.duration_ms,
      width=excluded.width,height=excluded.height,video_codec=excluded.video_codec,
      audio_codec=excluded.audio_codec,bitrate=excluded.bitrate,indexed_at=excluded.indexed_at,
      deleted=excluded.deleted,deleted_at=excluded.deleted_at
    """
    with db:
        for raw in paths:
            path = os.path.abspath(raw)
            if path in seen:
                continue
            seen.add(path)
            try:
                st = os.stat(path, follow_symlinks=False)
            except OSError:
                continue
            old_row = select("SELECT * FROM files WHERE path=?", (path,)).fetchone()
            old = dict(zip([c[0] for c in select("SELECT * FROM files LIMIT 0").description], old_row)) if old_row else None
            row = row_for(path, old)
            if row is not None:
                db.execute(upsert, row)
                changed += 1
            else:
                row = old
                if old and old.get("deleted"):
                    db.execute("UPDATE files SET deleted=0, deleted_at=0 WHERE path=?", (path,))
            output_kind = "d" if row["kind"] == "directory" else "f"
            if row.get("_crc_unreadable"):
                output_kind = "f!"
            print("%s\t%s\t%s\t%s\t%s\t%s" % (
                row["size"], row["mtime_ns"] / 1_000_000_000, output_kind,
                row["name"], row["path"], row["duration_ms"] or ""), flush=True)
        if seen:
            placeholders = ",".join("?" for _ in seen)
            # Only remove entries below paths that were actually scanned.
            parents = sorted({os.path.dirname(p) for p in seen})
            for parent in parents:
                stale = db.execute("SELECT path FROM files WHERE parent=?", (parent,)).fetchall()
                for (stale_path,) in stale:
                    if stale_path not in seen:
                        try:
                            os.stat(stale_path, follow_symlinks=False)
                        except OSError:
                            db.execute("UPDATE files SET deleted=1, deleted_at=? WHERE path=?", (int(time.time()), stale_path))
                            removed += 1
    return changed, removed


def main():
    ap = argparse.ArgumentParser(description="eazy incremental SQLite index")
    ap.add_argument("--db", required=True)
    ap.add_argument("--scan0", action="store_true", help="read NUL-separated paths from stdin")
    ap.add_argument("--query", action="store_true", help="query indexed files")
    ap.add_argument("--root", default="", help="query root")
    ap.add_argument("--ext", default="", help="space-separated extensions or TODAS")
    ap.add_argument("--min-size", type=int, default=0)
    ap.add_argument("--max-size", type=int, default=0)
    ap.add_argument("--show-deleted", action="store_true")
    ap.add_argument("--direct", action="store_true", help="query only direct children of root")
    ap.add_argument("--include-dirs", action="store_true")
    ap.add_argument("--lookup0", action="store_true", help="lookup de caminhos separados por NUL")
    ap.add_argument("--history-sync0", action="store_true", help="migra caminhos separados por NUL em stdin para history_items")
    ap.add_argument("--history-sync-file", metavar="PATH", help="recria history_items lendo o arquivo legado linha a linha")
    ap.add_argument("--history-list", action="store_true", help="lista os caminhos do histórico SQLite")
    ap.add_argument("--history-lookup", action="store_true", help="consulta metadados dos caminhos diretamente do histórico SQLite")
    ap.add_argument("--init", action="store_true")
    args = ap.parse_args()
    db = db_open(args.db)
    if args.init:
        db.close()
        return 0
    if args.history_sync0 or args.history_sync_file:
        if args.history_sync_file:
            # O histórico legado é texto UTF-8/bytes surrogate-escaped, uma entrada por linha.
            # Ler diretamente evita conversões newline/NUL sujeitas a quoting incorreto.
            raw = Path(args.history_sync_file).read_bytes()
            entries = raw.split(b"\n")
            if entries and entries[-1] == b"":
                entries.pop()
            paths = [entry.decode("utf-8", "surrogateescape") for entry in entries if entry]
        else:
            paths = [p.decode("utf-8", "surrogateescape") for p in sys.stdin.buffer.read().split(b"\0") if p]
        # O histórico é único por caminho; preserve a primeira ocorrência (mais recente) se
        # um arquivo legado antigo contiver duplicatas, respeitando a restrição SQL UNIQUE.
        unique_paths = []
        seen_paths = set()
        for path in paths:
            if path not in seen_paths:
                seen_paths.add(path)
                unique_paths.append(path)
        now = int(time.time())
        with db:
            db.execute("CREATE TABLE IF NOT EXISTS history_state (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
            db.execute("DELETE FROM history_items")
            db.executemany(
                "INSERT INTO history_items(path, position, played_at) VALUES (?, ?, ?)",
                [(path, pos, now - pos) for pos, path in enumerate(unique_paths)],
            )
            db.execute("INSERT OR REPLACE INTO history_state(key, value) VALUES ('migrated', '1')")
        db.close()
        return 0
    if args.history_list:
        for (path,) in db.execute("SELECT path FROM history_items ORDER BY position ASC, id ASC"):
            print(path, flush=True)
        db.close()
        return 0
    if args.history_lookup:
        rows = db.execute(
            "SELECT h.path, f.size, f.mtime_ns, f.kind, f.name, f.duration_ms, f.extension, f.deleted "
            "FROM history_items AS h LEFT JOIN files AS f ON f.path=h.path "
            "ORDER BY h.position ASC, h.id ASC"
        ).fetchall()
        for path, size, mtime_ns, kind, name, duration_ms, ext, deleted in rows:
            size = size or 0
            mtime_ns = mtime_ns or 0
            kind = kind or "other"
            name = name or os.path.basename(path)
            ext = ext or os.path.splitext(name)[1].lower()
            output_kind = "d" if kind == "directory" else "f"
            if deleted:
                output_kind = "x" if output_kind == "f" else "X"
            print(f"{size}\t{mtime_ns / 1_000_000_000}\t{output_kind}\t{name}\t{path}\t{duration_ms or ''}\t{ext}", flush=True)
        db.close()
        return 0
    if args.lookup0:
        paths = [p.decode("utf-8", "surrogateescape") for p in sys.stdin.buffer.read().split(b"\0") if p]
        if paths:
            marks = ",".join("?" for _ in paths)
            rows = db.execute(
                f"SELECT size,mtime_ns,kind,name,path,duration_ms,extension,deleted FROM files WHERE path IN ({marks})",
                paths,
            ).fetchall()
            for size, mtime_ns, kind, name, path, duration_ms, ext, deleted in rows:
                output_kind = "d" if kind == "directory" else "f"
                if deleted:
                    output_kind = "x" if output_kind == "f" else "X"
                print(f"{size}\t{mtime_ns / 1_000_000_000}\t{output_kind}\t{name}\t{path}\t{duration_ms or ''}\t{ext}", flush=True)
        db.close()
        return 0
    if args.scan0:
        raw = sys.stdin.buffer.read().split(b"\0")
        paths = [p.decode("utf-8", "surrogateescape") for p in raw if p]
        scan(db, paths)
    elif args.query:
        root = os.path.abspath(args.root or os.getcwd()).rstrip(os.sep) or os.sep
        indexed = db.execute("SELECT count(*) FROM files WHERE path=? OR path LIKE ?", (root, root + os.sep + "%")).fetchone()[0]
        if indexed == 0:
            db.close()
            return 2
        exts = {x.lower().lstrip(".") for x in args.ext.split() if x and x.upper() != "TODAS"}
        sql = "SELECT size, mtime_ns, kind, name, path, duration_ms, extension, deleted FROM files WHERE "
        if args.include_dirs:
            sql += "1=1"
        else:
            sql += "kind != 'directory'"
        if args.direct:
            sql += " AND parent=?"
            params = [root]
        else:
            sql += " AND (path=? OR path LIKE ?)"
            params = [root, root + os.sep + "%"]
        if not args.show_deleted:
            sql += " AND deleted=0"
        if exts:
            marks = ",".join("?" for _ in exts)
            sql += f" AND (kind='directory' OR lower(ltrim(extension, '.')) IN ({marks}))"
            params.extend(sorted(exts))
        if args.min_size:
            sql += " AND size > ?"
            params.append(args.min_size)
        if args.max_size:
            sql += " AND size < ?"
            params.append(args.max_size)
        # Diretórios ficam sempre no topo. Para diretórios, `size` é somente
        # o st_size da própria entrada; nunca somamos a árvore.
        if args.ext and args.ext.upper() != "TODAS":
            sql += " ORDER BY CASE WHEN kind='directory' THEN 0 ELSE 1 END, "
        else:
            sql += " ORDER BY CASE WHEN kind='directory' THEN 0 ELSE 1 END, "
        if args.max_size or args.min_size:
            sql += "size DESC, "
        sql += "name COLLATE NOCASE"
        for size, mtime_ns, kind, name, path, duration_ms, _ext, deleted in db.execute(sql, params):
            output_kind = "d" if kind == "directory" else "f"
            if deleted:
                output_kind = "x" if output_kind == "f" else "X"
            print(f"{size}\t{mtime_ns / 1_000_000_000}\t{output_kind}\t{name}\t{path}\t{duration_ms or ''}", flush=True)
    db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Persistent incremental file index for eazy.

The shell UI feeds paths separated by NUL on stdin.  The index stores cheap
filesystem identity/signature fields and media metadata.  CRC32 is internal
validation data only; it is never a user-facing sort key.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import sqlite3
import stat
import struct
import subprocess
import sys
import tempfile
import time
import zlib
from pathlib import Path
from types import SimpleNamespace

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
    deleted_at INTEGER NOT NULL DEFAULT 0,
    selected INTEGER NOT NULL DEFAULT 0 CHECK(selected IN (0,1,2))
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
CREATE TABLE IF NOT EXISTS directory_signatures (
    path TEXT PRIMARY KEY,
    signature TEXT NOT NULL,
    file_count INTEGER NOT NULL DEFAULT 0,
    total_bytes INTEGER NOT NULL DEFAULT 0,
    dir_count INTEGER NOT NULL DEFAULT 0,
    scanned_at INTEGER NOT NULL DEFAULT 0
);
"""

VIDEO = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".wmv", ".flv", ".m4v", ".mpg", ".mpeg"}
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
    tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if not {"files", "history_items"}.issubset(tables):
        db.executescript(SCHEMA)
    else:
        # WAL é persistente; synchronous é configuração por conexão.
        db.execute("PRAGMA synchronous=NORMAL")
    # Migração silenciosa de bancos criados antes da marca de exclusão.
    cols = {row[1] for row in db.execute("PRAGMA table_info(files)")}
    if "deleted" not in cols:
        db.execute("ALTER TABLE files ADD COLUMN deleted INTEGER NOT NULL DEFAULT 0")
    if "deleted_at" not in cols:
        db.execute("ALTER TABLE files ADD COLUMN deleted_at INTEGER NOT NULL DEFAULT 0")
    if "selected" not in cols:
        db.execute("ALTER TABLE files ADD COLUMN selected INTEGER NOT NULL DEFAULT 0")
    db.execute("CREATE INDEX IF NOT EXISTS idx_files_selected ON files(selected)")
    db.execute(
        "CREATE TABLE IF NOT EXISTS directory_signatures ("
        "path TEXT PRIMARY KEY, signature TEXT NOT NULL, "
        "file_count INTEGER NOT NULL DEFAULT 0, total_bytes INTEGER NOT NULL DEFAULT 0, "
        "dir_count INTEGER NOT NULL DEFAULT 0, scanned_at INTEGER NOT NULL DEFAULT 0)"
    )
    schema_version = db.execute("PRAGMA user_version").fetchone()[0]
    if schema_version < 1:
        db.execute(
            "UPDATE files SET kind='other',duration_ms=NULL,width=NULL,height=NULL,"
            "video_codec='',audio_codec='',bitrate=NULL "
            "WHERE extension='.ts' AND kind='video'"
        )
        db.execute("PRAGMA user_version=1")
    db.commit()
    return db


def db_readonly(path: str) -> sqlite3.Connection:
    uri = Path(path).resolve().as_uri() + "?mode=ro"
    return sqlite3.connect(uri, uri=True, timeout=30)


def selection_ensure_path(db: sqlite3.Connection, path: str) -> str:
    """Ensure a selected path has a files row, even if not yet indexed."""
    path = os.path.abspath(path)
    if db.execute("SELECT 1 FROM files WHERE path=?", (path,)).fetchone():
        return path
    st = os.stat(path, follow_symlinks=False)
    row = row_for(path, None, st)
    columns = (
        "path,name,parent,extension,kind,mime,size,mtime_ns,ctime_ns,device,inode,crc32,"
        "duration_ms,width,height,video_codec,audio_codec,bitrate,indexed_at,deleted,deleted_at,selected"
    )
    row["selected"] = 0
    values = [row.get(key) for key in columns.split(",")]
    db.execute(f"INSERT OR IGNORE INTO files({columns}) VALUES({','.join('?' for _ in values)})", values)
    return path


def selection_toggle_local(db: sqlite3.Connection, path: str) -> int:
    path = selection_ensure_path(db, path)
    with db:
        db.execute(
            "UPDATE files SET selected=CASE WHEN selected=0 THEN 1 ELSE 0 END WHERE path=?",
            (path,),
        )
    return db.execute("SELECT selected FROM files WHERE path=?", (path,)).fetchone()[0]


def selection_set(db: sqlite3.Connection, path: str, state: int) -> int:
    if state not in (0, 1, 2):
        raise ValueError("selected precisa ser 0, 1 ou 2")
    path = selection_ensure_path(db, path)
    with db:
        db.execute("UPDATE files SET selected=? WHERE path=?", (state, path))
    return state


def selection_invert0(db: sqlite3.Connection, raw: bytes) -> int:
    """Invert a unique NUL-delimited batch: 0 -> global(2), 1/2 -> 0."""
    paths = list(dict.fromkeys(
        item.decode("utf-8", "surrogateescape") for item in raw.split(b"\0") if item
    ))
    changed = 0
    with db:
        for item in paths:
            try:
                path = selection_ensure_path(db, item)
            except OSError:
                continue
            db.execute(
                "UPDATE files SET selected=CASE WHEN selected=0 THEN 2 ELSE 0 END WHERE path=?",
                (path,),
            )
            changed += 1
    return changed


def selection_toggle_all0(db: sqlite3.Connection, raw: bytes) -> str:
    """Toggle a visible batch: all selected -> clear, otherwise mark 0->1."""
    items = list(dict.fromkeys(
        item.decode("utf-8", "surrogateescape") for item in raw.split(b"\0") if item
    ))
    if not items:
        return "empty"
    paths: list[str] = []
    with db:
        for item in items:
            try:
                paths.append(selection_ensure_path(db, item))
            except OSError:
                continue
        if not paths:
            return "empty"
        states = [
            int(row[0]) for path in paths
            if (row := db.execute("SELECT selected FROM files WHERE path=?", (path,)).fetchone())
        ]
        if states and all(state != 0 for state in states):
            db.executemany("UPDATE files SET selected=0 WHERE path=?", ((path,) for path in paths))
            return "cleared"
        # Keep existing global marks (2); newly selected rows remain local (1).
        db.executemany(
            "UPDATE files SET selected=CASE WHEN selected=0 THEN 1 ELSE selected END WHERE path=?",
            ((path,) for path in paths),
        )
        return "selected"


def selection_count(db: sqlite3.Connection, state: int | None = None) -> int:
    if state is None:
        row = db.execute("SELECT count(*) FROM files WHERE selected<>0").fetchone()
    else:
        row = db.execute("SELECT count(*) FROM files WHERE selected=?", (state,)).fetchone()
    return int(row[0])


def selection_stats(db: sqlite3.Connection, state: int | None = 2) -> tuple[int, int, int]:
    sql = (
        "SELECT COUNT(*), COALESCE(SUM(size),0), "
        "COALESCE(SUM(kind='directory'),0) FROM files WHERE selected<>0"
    )
    params: tuple[object, ...] = ()
    if state is not None:
        sql += " AND selected=?"
        params = (state,)
    row = db.execute(sql, params).fetchone()
    return int(row[0]), int(row[1]), int(row[2])


def selection_ui_stats(db: sqlite3.Connection, root: str) -> tuple[int, int, int, int, int, int]:
    global_count, global_bytes, global_dirs = selection_stats(db, 2)
    root = os.path.abspath(root).rstrip(os.sep) or os.sep
    local_count, local_bytes, local_dirs = db.execute(
        "SELECT COUNT(*),COALESCE(SUM(size),0),COALESCE(SUM(kind='directory'),0) "
        "FROM files WHERE selected IN (1,2) AND (parent=? OR path=?)",
        (root, root),
    ).fetchone()
    return (int(global_count), int(global_bytes), int(global_dirs),
            int(local_count), int(local_bytes), int(local_dirs))


def selection_toggle_ui(db: sqlite3.Connection, path: str, root: str,
                        descendants: bytes = b"") -> tuple[int, tuple[int, int, int, int, int, int]]:
    state = selection_toggle_local(db, path)
    if descendants:
        with db:
            for raw_path in descendants.split(b"\0"):
                if not raw_path:
                    continue
                child = raw_path.decode("utf-8", "surrogateescape")
                try:
                    child = selection_ensure_path(db, child)
                except OSError:
                    continue
                db.execute("UPDATE files SET selected=? WHERE path=?", (state, child))
    return state, selection_ui_stats(db, root)


DUP_MARK_COLUMNS = {"selected": "selected", "fixed": "fixed"}


def duplicate_marks_ensure(db: sqlite3.Connection) -> None:
    db.execute(
        "CREATE TABLE IF NOT EXISTS eazy_duplicate_marks ("
        "session_id TEXT NOT NULL, path TEXT NOT NULL, "
        "selected INTEGER NOT NULL DEFAULT 0, fixed INTEGER NOT NULL DEFAULT 0, "
        "PRIMARY KEY(session_id,path))"
    )


def duplicate_marks_set0(db: sqlite3.Connection, session: str, kind: str, raw: bytes) -> int:
    column = DUP_MARK_COLUMNS.get(kind)
    if not column:
        raise ValueError("tipo de marca duplicada inválido")
    paths = list(dict.fromkeys(
        item.decode("utf-8", "surrogateescape") for item in raw.split(b"\0") if item
    ))
    duplicate_marks_ensure(db)
    with db:
        db.execute(f"UPDATE eazy_duplicate_marks SET {column}=0 WHERE session_id=?", (session,))
        db.executemany(
            f"INSERT INTO eazy_duplicate_marks(session_id,path,{column}) VALUES(?,?,1) "
            f"ON CONFLICT(session_id,path) DO UPDATE SET {column}=1",
            ((session, path) for path in paths),
        )
        db.execute(
            "DELETE FROM eazy_duplicate_marks WHERE session_id=? AND selected=0 AND fixed=0",
            (session,),
        )
    return len(paths)


def duplicate_marks_invert0(db: sqlite3.Connection, session: str, raw: bytes) -> int:
    paths = list(dict.fromkeys(
        item.decode("utf-8", "surrogateescape") for item in raw.split(b"\0") if item
    ))
    duplicate_marks_ensure(db)
    with db:
        db.executemany(
            "INSERT INTO eazy_duplicate_marks(session_id,path,selected) VALUES(?,?,1) "
            "ON CONFLICT(session_id,path) DO UPDATE SET selected=1-selected",
            ((session, path) for path in paths),
        )
        db.execute(
            "DELETE FROM eazy_duplicate_marks WHERE session_id=? AND selected=0 AND fixed=0",
            (session,),
        )
    return len(paths)


def duplicate_marks_toggle(db: sqlite3.Connection, session: str, path: str) -> int:
    duplicate_marks_ensure(db)
    with db:
        db.execute(
            "INSERT INTO eazy_duplicate_marks(session_id,path,selected) VALUES(?,?,1) "
            "ON CONFLICT(session_id,path) DO UPDATE SET selected=1-selected",
            (session, os.path.abspath(path)),
        )
        row = db.execute(
            "SELECT selected FROM eazy_duplicate_marks WHERE session_id=? AND path=?",
            (session, os.path.abspath(path)),
        ).fetchone()
        db.execute(
            "DELETE FROM eazy_duplicate_marks WHERE session_id=? AND path=? AND selected=0 AND fixed=0",
            (session, os.path.abspath(path)),
        )
    return int(row[0])


def duplicate_marks_clear(db: sqlite3.Connection, session: str, kind: str) -> int:
    duplicate_marks_ensure(db)
    with db:
        if kind == "all":
            cur = db.execute("DELETE FROM eazy_duplicate_marks WHERE session_id=?", (session,))
        elif kind in DUP_MARK_COLUMNS:
            column = DUP_MARK_COLUMNS[kind]
            cur = db.execute(
                f"UPDATE eazy_duplicate_marks SET {column}=0 WHERE session_id=?", (session,)
            )
            db.execute(
                "DELETE FROM eazy_duplicate_marks WHERE session_id=? AND selected=0 AND fixed=0",
                (session,),
            )
        else:
            raise ValueError("tipo de marca duplicada inválido")
    return cur.rowcount


def duplicate_marks_copy_fixed(db: sqlite3.Connection, session: str) -> int:
    duplicate_marks_ensure(db)
    with db:
        cur = db.execute(
            "UPDATE eazy_duplicate_marks SET selected=1 WHERE session_id=? AND fixed=1 AND selected=0",
            (session,),
        )
    return cur.rowcount


def duplicate_marks_list0(db: sqlite3.Connection, session: str, kind: str) -> None:
    column = DUP_MARK_COLUMNS.get(kind)
    if not column:
        raise ValueError("tipo de marca duplicada inválido")
    if db.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='eazy_duplicate_marks'"
    ).fetchone() is None:
        return
    for (path,) in db.execute(
        f"SELECT path FROM eazy_duplicate_marks WHERE session_id=? AND {column}=1 ORDER BY path",
        (session,),
    ):
        sys.stdout.buffer.write(path.encode("utf-8", "surrogateescape") + b"\0")


def duplicate_marks_stats(db: sqlite3.Connection, session: str) -> tuple[int, int]:
    if db.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='eazy_duplicate_marks'"
    ).fetchone() is None:
        return 0, 0
    if db.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='eazy_duplicate_results'"
    ).fetchone() is None:
        return 0, 0
    row = db.execute(
        "SELECT count(*), COALESCE(sum(COALESCE(r.size,0)),0) "
        "FROM eazy_duplicate_marks d LEFT JOIN eazy_duplicate_results r ON r.path=d.path "
        "WHERE d.session_id=? AND d.selected=1", (session,)
    ).fetchone()
    return int(row[0]), int(row[1])


def duplicate_results_ensure(db: sqlite3.Connection) -> None:
    db.execute(
        "CREATE TABLE IF NOT EXISTS eazy_duplicate_results ("
        "ordinal INTEGER PRIMARY KEY, hash TEXT NOT NULL, size INTEGER NOT NULL, path TEXT NOT NULL)"
    )


def duplicate_results_replace(db: sqlite3.Connection, rows) -> int:
    """Replace persisted search results; paths are SQL text and may contain tabs/newlines."""
    normalized = [(str(digest), int(size), str(path)) for digest, size, path in rows]
    duplicate_results_ensure(db)
    with db:
        db.execute("DELETE FROM eazy_duplicate_results")
        db.executemany(
            "INSERT INTO eazy_duplicate_results(ordinal,hash,size,path) VALUES(?,?,?,?)",
            ((ordinal, digest, size, path) for ordinal, (digest, size, path) in enumerate(normalized)),
        )
    return len(normalized)


def duplicate_results_import(db: sqlite3.Connection, path: str) -> int:
    """Importa o TSV legado hash<TAB>tamanho<TAB>caminho, preservando a ordem."""
    rows = []
    source = Path(path)
    if source.is_file():
        for line in source.read_bytes().splitlines():
            if not line:
                continue
            fields = line.split(b"\t", 2)
            if len(fields) != 3:
                raise ValueError("linha TSV de duplicados inválida; esperados hash, size, path")
            digest, size, item_path = fields
            rows.append((digest.decode("utf-8", "surrogateescape"), int(size),
                         item_path.decode("utf-8", "surrogateescape")))
    return duplicate_results_replace(db, rows)


def duplicate_results_init(db: sqlite3.Connection, legacy_path: str = "") -> int:
    existed = db.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='eazy_duplicate_results'"
    ).fetchone() is not None
    duplicate_results_ensure(db)
    if existed:
        return 0
    return duplicate_results_import(db, legacy_path) if legacy_path else 0


def duplicate_results_export(db: sqlite3.Connection) -> None:
    if db.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='eazy_duplicate_results'"
    ).fetchone() is None:
        return
    for digest, size, path in db.execute(
        "SELECT hash,size,path FROM eazy_duplicate_results ORDER BY ordinal"
    ):
        line = f"{digest}\t{size}\t{path}\n"
        sys.stdout.buffer.write(line.encode("utf-8", "surrogateescape"))


def duplicate_results_clear(db: sqlite3.Connection) -> int:
    if db.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='eazy_duplicate_results'"
    ).fetchone() is None:
        return 0
    with db:
        return db.execute("DELETE FROM eazy_duplicate_results").rowcount


def duplicate_results_remove(db: sqlite3.Connection, path: str) -> int:
    if db.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='eazy_duplicate_results'"
    ).fetchone() is None:
        return 0
    with db:
        rows = db.execute(
            "SELECT hash,size,path FROM eazy_duplicate_results WHERE path<>? ORDER BY ordinal", (path,)
        ).fetchall()
        removed = db.execute("SELECT count(*) FROM eazy_duplicate_results WHERE path=?", (path,)).fetchone()[0]
        if removed:
            db.execute("DELETE FROM eazy_duplicate_results")
            db.executemany(
                "INSERT INTO eazy_duplicate_results(ordinal,hash,size,path) VALUES(?,?,?,?)",
                ((ordinal, digest, size, item_path) for ordinal, (digest, size, item_path) in enumerate(rows)),
            )
    return int(removed)


def selection_promote(db: sqlite3.Connection, root: str = "") -> int:
    """Promote immediate selections (1) to persistent global selections (2)."""
    with db:
        if root:
            exact = os.path.abspath(root).rstrip(os.sep)
            root = exact + os.sep
            cur = db.execute(
                "UPDATE files SET selected=2 WHERE selected=1 AND (path=? OR substr(path,1,?)=?)",
                (exact, len(root), root),
            )
        else:
            cur = db.execute("UPDATE files SET selected=2 WHERE selected=1")
    return cur.rowcount


def selection_clear(db: sqlite3.Connection, state: int | None = None, root: str = "") -> int:
    clauses = ["selected<>0"]
    params: list[object] = []
    if state is not None:
        if state not in (1, 2):
            raise ValueError("estado para limpar precisa ser 1 ou 2")
        clauses.append("selected=?")
        params.append(state)
    if root:
        exact = os.path.abspath(root).rstrip(os.sep)
        root = exact + os.sep
        clauses.append("(path=? OR substr(path,1,?)=?)")
        params.extend([exact, len(root), root])
    with db:
        cur = db.execute("UPDATE files SET selected=0 WHERE " + " AND ".join(clauses), params)
    return cur.rowcount


def selection_import_file(db: sqlite3.Connection, path: str) -> int:
    """Import the pre-SQL global selection once; leave the legacy file untouched."""
    with db:
        db.execute("CREATE TABLE IF NOT EXISTS eazy_selection_state(key TEXT PRIMARY KEY,value TEXT NOT NULL)")
        if db.execute("SELECT 1 FROM eazy_selection_state WHERE key='legacy_imported'").fetchone():
            return 0
        imported = 0
        legacy = Path(path)
        if legacy.is_file():
            for raw in legacy.read_bytes().splitlines():
                if not raw:
                    continue
                item = raw.decode("utf-8", "surrogateescape")
                try:
                    item = selection_ensure_path(db, item)
                except OSError:
                    # Keep unavailable legacy entries in the untouched source file.
                    continue
                db.execute("UPDATE files SET selected=2 WHERE path=? AND selected=0", (item,))
                imported += 1
        db.execute("INSERT INTO eazy_selection_state(key,value) VALUES('legacy_imported','1')")
    return imported


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


def row_for(path: str, old, st=None):
    st = st or os.stat(path, follow_symlinks=False)
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
    signature = (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns)
    old_signature = None
    if old:
        old_signature = (
            old["device"], old["inode"], old["size"], old["mtime_ns"], old["ctime_ns"]
        )
    changed = old is None or signature != old_signature or old.get("kind") != kind
    if not changed:
        return None
    mime = mimetypes.guess_type(name, strict=False)[0] or ""
    # CRC não é calculado na indexação: isso exigiria ler o arquivo inteiro.
    # A validação forte ficará restrita aos candidatos da pesquisa de duplicados.
    crc = ""
    crc_unreadable = False
    # A atualização normal é só filesystem/SQL: não inicia ffprobe por arquivo.
    # Duração/codec ficam vazios em novos/alterados; a leitura antiga fica intacta
    # enquanto a assinatura do arquivo não mudar.
    media = {"duration_ms": None, "width": None, "height": None,
             "video_codec": "", "audio_codec": "", "bitrate": None}
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


def iter_nul_paths(stream):
    """Yield NUL-separated paths without loading the whole scan into memory."""
    remainder = b""
    while True:
        chunk = stream.read(1024 * 1024)
        if not chunk:
            break
        parts = (remainder + chunk).split(b"\0")
        remainder = parts.pop()
        for raw in parts:
            if raw:
                yield raw.decode("utf-8", "surrogateescape")
    if remainder:
        yield remainder.decode("utf-8", "surrogateescape")


def write_progress(progress_file: str, processed: int, path: str,
                   phase: str = "indexando", total: int = 0) -> None:
    target = Path(progress_file)
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_name(target.name + f".{os.getpid()}.tmp")
    display_path = str(path).replace("\t", "\\t").replace("\r", "\\r").replace("\n", "\\n")
    with temp.open("w", encoding="utf-8", errors="replace") as fh:
        fh.write(f"{phase}\t{processed}\t{total}\t{display_path}\n")
    os.replace(temp, target)


def scan(db: sqlite3.Connection, paths, progress_file=None, quiet=False,
         delete_parents=None, preloaded_stats=None, exclude_path=None,
         total_count=0, deduplicate_paths=True):
    seen = set() if deduplicate_paths else None
    processed = changed = removed = revived = 0
    last_progress = 0.0
    preloaded_stats = preloaded_stats or {}
    excluded = os.path.realpath(exclude_path) if exclude_path else ""
    select = db.execute
    old_columns = ("device", "inode", "size", "mtime_ns", "ctime_ns", "deleted",
                   "kind", "name", "path", "duration_ms")
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
            if isinstance(raw, tuple):
                raw_path, supplied_stat = raw
            else:
                raw_path, supplied_stat = raw, None
            path = os.path.abspath(raw_path)
            if excluded and (path == excluded or path.startswith(excluded.rstrip(os.sep) + os.sep)):
                continue
            if seen is not None:
                if path in seen:
                    continue
                seen.add(path)
            processed += 1
            st = supplied_stat or preloaded_stats.get(path)
            try:
                st = st or os.stat(path, follow_symlinks=False)
            except OSError:
                st = None
            if st is not None:
                old_row = select(
                    "SELECT device,inode,size,mtime_ns,ctime_ns,deleted,kind,name,path,duration_ms "
                    "FROM files WHERE path=?", (path,)
                ).fetchone()
                old = dict(zip(old_columns, old_row)) if old_row else None
                row = row_for(path, old, st)
                if row is not None:
                    db.execute(upsert, row)
                    changed += 1
                else:
                    row = old
                    if old and old.get("deleted"):
                        db.execute("UPDATE files SET deleted=0, deleted_at=0 WHERE path=?", (path,))
                        row["deleted"] = 0
                        revived += 1
                if not quiet and row:
                    output_kind = "d" if row["kind"] == "directory" else "f"
                    print("%s\t%s\t%s\t%s\t%s\t%s" % (
                        row["size"], row["mtime_ns"] // 1_000_000_000, output_kind,
                        row["name"], row["path"], row["duration_ms"] or ""))
            if progress_file:
                now = time.monotonic()
                if processed % 128 == 0 or now - last_progress >= 0.5:
                    write_progress(progress_file, processed, path, "indexando", total_count)
                    last_progress = now

        if delete_parents is None:
            parents = sorted({os.path.dirname(p) for p in seen}) if seen is not None else []
        else:
            parents = sorted({os.path.abspath(p) for p in delete_parents})
        if parents:
            now = int(time.time())
            cleanup_checked = 0
            cleanup_last_progress = 0.0
            cleanup_total = len(parents)
            for parent_number, parent in enumerate(parents, 1):
                if progress_file:
                    write_progress(progress_file, cleanup_checked, parent,
                                   "limpando", cleanup_total)
                stale = db.execute(
                    "SELECT path,kind,deleted FROM files WHERE parent=?", (parent,)
                ).fetchall()
                for stale_path, kind, was_deleted in stale:
                    cleanup_checked += 1
                    if progress_file:
                        progress_now = time.monotonic()
                        if cleanup_checked % 128 == 0 or progress_now - cleanup_last_progress >= 0.5:
                            write_progress(progress_file, cleanup_checked, parent,
                                           "limpando", cleanup_total)
                            cleanup_last_progress = progress_now
                    if (seen is not None and stale_path in seen) or was_deleted:
                        continue
                    try:
                        os.stat(stale_path, follow_symlinks=False)
                    except (FileNotFoundError, NotADirectoryError):
                        db.execute(
                            "UPDATE files SET deleted=1, deleted_at=? WHERE path=? AND deleted=0",
                            (now, stale_path),
                        )
                        removed += 1
                        if kind == "directory":
                            prefix = stale_path.rstrip(os.sep) + os.sep
                            cur = db.execute(
                                "UPDATE files SET deleted=1, deleted_at=? "
                                "WHERE deleted=0 AND substr(path,1,?)=?",
                                (now, len(prefix), prefix),
                            )
                            removed += cur.rowcount
                    except OSError:
                        # Permission/IO failures are not proof of deletion.
                        pass
                if progress_file and (parent_number == 1 or parent_number % 32 == 0):
                    write_progress(progress_file, cleanup_checked, parent,
                                   "limpando", cleanup_total)
    if progress_file:
        write_progress(progress_file, processed, "", "indexando", total_count)
    if not quiet:
        sys.stdout.flush()
    return {"processed": processed, "changed": changed, "removed": removed, "revived": revived}


def _md5_digest():
    try:
        return hashlib.md5(usedforsecurity=False)
    except TypeError:  # Python < 3.9
        return hashlib.md5()


def _new_directory_accumulator():
    # count, sum(entry MD5), xor(entry MD5), files, bytes, directories.
    return [0, 0, 0, 0, 0, 0]


def _add_directory_entry(accumulator, path: str, st) -> None:
    """Add one regular file/directory to a commutative MD5 listing fingerprint."""
    is_dir = stat.S_ISDIR(st.st_mode)
    if not is_dir and not stat.S_ISREG(st.st_mode):
        return
    name = os.fsencode(os.path.basename(path))
    fields = (st.st_mode, st.st_nlink, st.st_uid, st.st_gid, st.st_size,
              st.st_mtime_ns, st.st_ctime_ns, st.st_dev, st.st_ino)
    entry = _md5_digest()
    entry.update(b"eazy-directory-entry-v2\0")
    entry.update(len(name).to_bytes(8, "big"))
    entry.update(name)
    entry.update(("|".join(map(str, fields)) + "\n").encode("ascii"))
    value = int.from_bytes(entry.digest(), "big")
    accumulator[0] += 1
    accumulator[1] = (accumulator[1] + value) & ((1 << 128) - 1)
    accumulator[2] ^= value
    if is_dir:
        accumulator[5] += 1
    else:
        accumulator[3] += 1
        accumulator[4] += st.st_size


def _finish_directory_signature(root_st, accumulator) -> str:
    digest = _md5_digest()
    digest.update(b"eazy-directory-signature-v2\0")
    root_meta = (root_st.st_mode, root_st.st_size, root_st.st_mtime_ns,
                 root_st.st_ctime_ns, root_st.st_dev, root_st.st_ino,
                 root_st.st_uid, root_st.st_gid)
    digest.update(("|".join(map(str, root_meta)) + "\n").encode("ascii"))
    digest.update(("|".join(map(str, accumulator[:3])) + "\n").encode("ascii"))
    return digest.hexdigest()


def directory_snapshot(root: str, root_st=None, exclude_path=None):
    """Read one directory once, returning its MD5 signature, entries and counts."""
    root = os.path.abspath(root)
    root_st = root_st or os.stat(root, follow_symlinks=False)
    if not stat.S_ISDIR(root_st.st_mode):
        raise NotADirectoryError(root)
    excluded = os.path.realpath(exclude_path) if exclude_path else ""
    excluded_prefix = excluded.rstrip(os.sep) + os.sep if excluded else ""
    accumulator = _new_directory_accumulator()
    children = []
    with os.scandir(root) as entries:
        for entry in entries:
            path = os.path.abspath(entry.path)
            if excluded and (path == excluded or path.startswith(excluded_prefix)):
                continue
            try:
                st = entry.stat(follow_symlinks=False)
            except OSError as exc:
                raise OSError(f"Não foi possível conferir {entry.path}: {exc}") from exc
            if stat.S_ISDIR(st.st_mode) or stat.S_ISREG(st.st_mode):
                children.append((path, st))
                _add_directory_entry(accumulator, path, st)
    signature = _finish_directory_signature(root_st, accumulator)
    counts = (accumulator[3], accumulator[4], accumulator[5])
    return root_st, signature, children, counts


def directory_metadata_signature(root: str, exclude_path=None):
    """Return the v2 MD5 signature of this directory's immediate indexed entries."""
    root_st, signature, _children, _counts = directory_snapshot(
        root, exclude_path=exclude_path
    )
    return root_st, signature


def sync_directory(db: sqlite3.Connection, root: str, exclude_path=None,
                   watch_root: str = "", watch_queue_dir: str = ""):
    root = os.path.abspath(root)
    excluded = os.path.realpath(exclude_path) if exclude_path else ""
    if excluded and (root == excluded or root.startswith(excluded.rstrip(os.sep) + os.sep)):
        return {"processed": 0, "changed": 0, "removed": 0, "revived": 0,
                "files": 0, "bytes": 0}
    # O watcher só pode dispensar o hash raso quando a pasta já tem assinatura
    # (a árvore inicial pode não ter sido varrida) e não há tickets aguardando.
    if watch_root and watch_queue_dir:
        covered_root = os.path.abspath(watch_root).rstrip(os.sep) or os.sep
        covered = (covered_root == os.sep or root == covered_root or
                   root.startswith(covered_root.rstrip(os.sep) + os.sep))
        queue = Path(watch_queue_dir)
        try:
            if covered and queue.is_dir() and next(queue.glob("*.evt"), None) is None:
                cached = db.execute(
                    "SELECT file_count,total_bytes,dir_count FROM directory_signatures WHERE path=?",
                    (root,),
                ).fetchone()
                if cached:
                    return {"processed": cached[0] + cached[2] + 1, "changed": 0,
                            "removed": 0, "revived": 0, "files": cached[0],
                            "bytes": cached[1]}
        except (OSError, sqlite3.Error):
            # Falha de verificação nunca autoriza ignorar a reconciliação normal.
            pass
    root_st, signature, children, counts = directory_snapshot(
        root, exclude_path=excluded
    )

    cached = db.execute(
        "SELECT signature,file_count,total_bytes,dir_count FROM directory_signatures WHERE path=?",
        (root,),
    ).fetchone()
    if cached and cached[0] == signature:
        return {"processed": cached[1] + cached[3] + 1, "changed": 0, "removed": 0,
                "revived": 0, "files": cached[1], "bytes": cached[2]}

    # Only a changed signature pays for the detailed scan and SQLite row updates.
    paths = [root]
    preloaded_stats = {root: root_st}
    for path, st in children:
        paths.append(path)
        preloaded_stats[path] = st
    result = scan(db, paths, quiet=True, delete_parents={root},
                  preloaded_stats=preloaded_stats, exclude_path=excluded)
    file_count, total_bytes, dir_count = counts
    with db:
        db.execute(
            "INSERT INTO directory_signatures(path,signature,file_count,total_bytes,dir_count,scanned_at) "
            "VALUES(?,?,?,?,?,?) ON CONFLICT(path) DO UPDATE SET "
            "signature=excluded.signature,file_count=excluded.file_count, "
            "total_bytes=excluded.total_bytes,dir_count=excluded.dir_count,scanned_at=excluded.scanned_at",
            (root, signature, file_count, total_bytes, dir_count, int(time.time())),
        )
    result.update({"files": file_count, "bytes": total_bytes})
    return result


def scan_tree(db: sqlite3.Connection, root: str, progress_file=None,
              exclude_path=None):
    """Incrementally index a tree using one shallow MD5 signature per directory.

    Every directory is visited once to inspect its immediate entries. Files in an
    unchanged directory are not sent through the SQLite row updater; child
    directories are still checked independently so deep changes are detected.
    """
    root = os.path.abspath(root)
    excluded = os.path.realpath(exclude_path) if exclude_path else ""
    excluded_prefix = excluded.rstrip(os.sep) + os.sep if excluded else ""
    if excluded and (root == excluded or root.startswith(excluded_prefix)):
        raise ValueError("A pasta de configuração não pode ser o ponto inicial")
    root_st = os.stat(root, follow_symlinks=False)
    if not stat.S_ISDIR(root_st.st_mode):
        raise NotADirectoryError(root)
    root_device = root_st.st_dev
    stack = [(root, root_st)]
    changed_dirs = set()
    pending_signatures = {}
    scheduled_dirs = set()
    checked_dirs = unchanged_dirs = path_count = 0
    last_progress = 0.0
    record_header = struct.Struct(">I6q")

    def add_record(spool, path, st):
        nonlocal path_count
        if stat.S_ISDIR(st.st_mode):
            if path in scheduled_dirs:
                return
            scheduled_dirs.add(path)
        path_bytes = os.fsencode(path)
        spool.write(record_header.pack(
            len(path_bytes), st.st_mode, st.st_size, st.st_mtime_ns,
            st.st_ctime_ns, st.st_dev, st.st_ino,
        ))
        spool.write(path_bytes)
        path_count += 1

    with tempfile.TemporaryFile(mode="w+b") as path_spool:
        while stack:
            current, current_st = stack.pop()
            if excluded and (current == excluded or current.startswith(excluded_prefix)):
                continue
            _root_st, signature, children, counts = directory_snapshot(
                current, current_st, exclude_path=excluded
            )
            checked_dirs += 1
            cached = db.execute(
                "SELECT signature FROM directory_signatures WHERE path=?", (current,)
            ).fetchone()
            changed = not cached or cached[0] != signature
            if changed:
                changed_dirs.add(current)
                pending_signatures[current] = (signature, *counts)
                add_record(path_spool, current, current_st)
                for child, child_st in children:
                    add_record(path_spool, child, child_st)
            else:
                unchanged_dirs += 1
                if current == root:
                    # Keep the chosen root row present even when its contents are cached.
                    add_record(path_spool, current, current_st)
            for child, child_st in reversed(children):
                if stat.S_ISDIR(child_st.st_mode) and child_st.st_dev == root_device:
                    stack.append((child, child_st))
            if progress_file:
                now = time.monotonic()
                if checked_dirs == 1 or checked_dirs % 32 == 0 or now - last_progress >= 0.5:
                    write_progress(progress_file, checked_dirs, current,
                                   "verificando", 0)
                    last_progress = now

        def iter_spooled_paths():
            path_spool.seek(0)
            while True:
                raw_header = path_spool.read(record_header.size)
                if not raw_header:
                    return
                if len(raw_header) != record_header.size:
                    raise OSError("Registro temporário de indexação truncado")
                length, mode, size, mtime_ns, ctime_ns, device, inode = record_header.unpack(raw_header)
                raw_path = path_spool.read(length)
                if len(raw_path) != length:
                    raise OSError("Caminho temporário de indexação truncado")
                path = os.fsdecode(raw_path)
                st = SimpleNamespace(st_mode=mode, st_size=size, st_mtime_ns=mtime_ns,
                                     st_ctime_ns=ctime_ns, st_dev=device, st_ino=inode)
                yield path, st

        if progress_file:
            write_progress(progress_file, 0, root, "indexando", path_count)
        result = scan(
            db, iter_spooled_paths(), progress_file=progress_file, quiet=True,
            delete_parents=changed_dirs, exclude_path=excluded,
            total_count=path_count, deduplicate_paths=False,
        )
    if pending_signatures:
        now = int(time.time())
        signature_sql = (
            "INSERT INTO directory_signatures(path,signature,file_count,total_bytes,dir_count,scanned_at) "
            "VALUES(?,?,?,?,?,?) ON CONFLICT(path) DO UPDATE SET "
            "signature=excluded.signature,file_count=excluded.file_count, "
            "total_bytes=excluded.total_bytes,dir_count=excluded.dir_count,scanned_at=excluded.scanned_at"
        )
        with db:
            for number, (directory, values) in enumerate(pending_signatures.items(), 1):
                db.execute(signature_sql, (directory, *values, now))
                if progress_file and (number == 1 or number % 128 == 0):
                    write_progress(progress_file, number, directory,
                                   "assinando", len(pending_signatures))
    if progress_file:
        write_progress(progress_file, result["processed"], root,
                       "concluido", result["processed"])
    result.update({"checked_directories": checked_dirs,
                   "unchanged_directories": unchanged_dirs,
                   "updated_signatures": len(pending_signatures)})
    return result


LIST_FIXED = ("temp_playlist_1", "temp_playlist_2", "temp_playlist_3")
LIST_REGISTRY = "eazy_list_migrations"
LAST_SEARCH_TABLE = "eazy_internal_last_search"
LAST_SEARCH_SOURCE = "@eazy-internal:last-search"
LIST_RESERVED = {"files", "history_items", "history_state", LIST_REGISTRY, LAST_SEARCH_TABLE}


def quote_identifier(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def list_registry_ensure(db: sqlite3.Connection) -> None:
    db.execute(
        f"CREATE TABLE IF NOT EXISTS {quote_identifier(LIST_REGISTRY)} ("
        "table_name TEXT PRIMARY KEY, source_file TEXT NOT NULL UNIQUE, "
        "source_sha256 TEXT NOT NULL, entry_count INTEGER NOT NULL, migrated_at TEXT NOT NULL)"
    )
    columns = {row[1] for row in db.execute(f"PRAGMA table_info({quote_identifier(LIST_REGISTRY)})")}
    required = {"table_name", "source_file", "source_sha256", "entry_count", "migrated_at"}
    if not required.issubset(columns):
        raise ValueError(f"esquema inesperado em {LIST_REGISTRY}")
    if "revision" not in columns:
        db.execute(
            f"ALTER TABLE {quote_identifier(LIST_REGISTRY)} "
            "ADD COLUMN revision INTEGER NOT NULL DEFAULT 0"
        )


def list_table_names(db: sqlite3.Connection) -> dict[str, str]:
    return {
        name.casefold(): name
        for (name,) in db.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }


def list_table_validate(db: sqlite3.Connection, table: str) -> None:
    row = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=? COLLATE NOCASE",
        (table,),
    ).fetchone()
    if row is None:
        raise ValueError(f"a tabela de lista {table!r} não existe; execute a migração antes de usar o Easy")
    existing = row[0]
    columns = [row[1] for row in db.execute(f"PRAGMA table_info({quote_identifier(existing)})")]
    if columns != ["position", "path"]:
        raise ValueError(f"a tabela de lista {existing!r} tem esquema inesperado")


def list_source_targets(source_dir: str) -> dict[str, str]:
    directory = Path(source_dir).expanduser()
    sources: dict[str, str] = {}
    for table in LIST_FIXED:
        if (directory / table).is_file():
            sources[table.casefold()] = table
    # Compatibilidade com a fila singular usada por versões antigas.
    if (directory / "temp_playlist").is_file() and "temp_playlist_1" not in sources:
        sources["temp_playlist_1"] = "temp_playlist"
    for path in directory.glob("temp_playlist_custom_*"):
        if path.is_file():
            name = path.name[len("temp_playlist_custom_"):]
            if name:
                sources[name.casefold()] = path.name
    return sources


def list_initialize(db: sqlite3.Connection, source_dir: str) -> None:
    # Startup normal: depois que a migração inicial criou o registry e as filas
    # fixas, não varrer ~/.config/eazy nem validar cada lista customizada. As
    # listas customizadas continuam sendo validadas quando abertas individualmente.
    has_registry = db.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? COLLATE NOCASE",
        (LIST_REGISTRY,),
    ).fetchone() is not None
    has_fixed = all(
        db.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? COLLATE NOCASE",
            (name,),
        ).fetchone() is not None
        for name in LIST_FIXED
    )
    if has_registry and has_fixed:
        for name in LIST_FIXED:
            list_table_validate(db, name)
        return
    names = list_table_names(db)
    registered = {
        row[0].casefold(): row[0]
        for row in db.execute(
            f"SELECT table_name FROM {quote_identifier(LIST_REGISTRY)}"
        )
    } if LIST_REGISTRY in names else {}
    legacy = list_source_targets(source_dir)
    unresolved = [source for target, source in legacy.items() if target not in names]
    if unresolved:
        details = ", ".join(sorted(set(legacy.values())))
        raise ValueError(
            "foram encontrados arquivos de listas antigas, mas faltam tabelas SQLite "
            f"({details}); feche o Easy e execute migrate_eazy_lists.py --apply antes de abrir as listas"
        )

    list_registry_ensure(db)
    with db:
        for name in LIST_FIXED:
            actual = list_table_names(db).get(name.casefold())
            if actual is None:
                db.execute(
                    f"CREATE TABLE {quote_identifier(name)} "
                    "(position INTEGER PRIMARY KEY, path TEXT NOT NULL)"
                )
                actual = name
            list_table_validate(db, actual)
            if actual.casefold() not in registered:
                db.execute(
                    f"INSERT INTO {quote_identifier(LIST_REGISTRY)} "
                    "(table_name,source_file,source_sha256,entry_count,migrated_at,revision) "
                    "VALUES(?,?,?,?,?,0)",
                    (actual, "@eazy-sql:" + actual, "", 0, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())),
                )
        rows = db.execute(
            f"SELECT table_name FROM {quote_identifier(LIST_REGISTRY)} ORDER BY table_name COLLATE NOCASE"
        ).fetchall()
        for (table,) in rows:
            list_table_validate(db, table)


def list_registered(db: sqlite3.Connection, table: str) -> str:
    row = db.execute(
        f"SELECT table_name FROM {quote_identifier(LIST_REGISTRY)} WHERE table_name=? COLLATE NOCASE",
        (table,),
    ).fetchone()
    if not row:
        raise ValueError(f"a lista SQLite {table!r} não está registrada")
    list_table_validate(db, row[0])
    return row[0]


def list_touch_revision(db: sqlite3.Connection, table: str) -> None:
    quoted = quote_identifier(table)
    count = db.execute(f"SELECT count(*) FROM {quoted}").fetchone()[0]
    db.execute(
        f"UPDATE {quote_identifier(LIST_REGISTRY)} "
        "SET revision=revision+1, entry_count=? WHERE table_name=? COLLATE NOCASE",
        (count, table),
    )


def list_create(db: sqlite3.Connection, table: str) -> None:
    if not table or "\x00" in table or "\n" in table or "\r" in table or "\t" in table:
        raise ValueError("o nome da lista está vazio ou contém um caractere de controle")
    if table.casefold().startswith("sqlite_") or table.casefold() in LIST_RESERVED:
        raise ValueError(f"o nome {table!r} é reservado pelo SQLite/Easy")
    list_registry_ensure(db)
    if list_table_names(db).get(table.casefold()) is not None:
        raise ValueError(f"já existe uma tabela/lista chamada {table!r}")
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with db:
        db.execute(
            f"CREATE TABLE {quote_identifier(table)} (position INTEGER PRIMARY KEY, path TEXT NOT NULL)"
        )
        db.execute(
            f"INSERT INTO {quote_identifier(LIST_REGISTRY)} "
            "(table_name,source_file,source_sha256,entry_count,migrated_at,revision) "
            "VALUES(?,?,?,?,?,0)",
            (table, "@eazy-sql:" + table, "", 0, stamp),
        )


def list_append0(db: sqlite3.Connection, table: str, raw: bytes) -> int:
    table = list_registered(db, table)
    paths = [part.decode("utf-8", "surrogateescape") for part in raw.split(b"\0") if part]
    quoted = quote_identifier(table)
    added = 0
    with db:
        existing = {row[0] for row in db.execute(f"SELECT path FROM {quoted}")}
        next_position = db.execute(f"SELECT COALESCE(MAX(position),-1)+1 FROM {quoted}").fetchone()[0]
        for path in paths:
            if path in existing:
                continue
            db.execute(f"INSERT INTO {quoted}(position,path) VALUES(?,?)", (next_position, path))
            next_position += 1
            existing.add(path)
            added += 1
        if added:
            list_touch_revision(db, table)
    return added


def list_remove0(db: sqlite3.Connection, table: str, raw: bytes) -> int:
    table = list_registered(db, table)
    paths = {part.decode("utf-8", "surrogateescape") for part in raw.split(b"\0") if part}
    if not paths:
        return 0
    quoted = quote_identifier(table)
    with db:
        rows = db.execute(f"SELECT position,path FROM {quoted} ORDER BY position").fetchall()
        kept = [path for _position, path in rows if path not in paths]
        removed = len(rows) - len(kept)
        if removed:
            db.execute(f"DELETE FROM {quoted}")
            db.executemany(
                f"INSERT INTO {quoted}(position,path) VALUES(?,?)",
                enumerate(kept),
            )
            list_touch_revision(db, table)
    return removed


def list_replace0(db: sqlite3.Connection, table: str, raw: bytes) -> int:
    table = list_registered(db, table)
    paths = [part.decode("utf-8", "surrogateescape") for part in raw.split(b"\0") if part]
    quoted = quote_identifier(table)
    with db:
        current = [row[0] for row in db.execute(f"SELECT path FROM {quoted} ORDER BY position")]
        if current != paths:
            db.execute(f"DELETE FROM {quoted}")
            db.executemany(
                f"INSERT INTO {quoted}(position,path) VALUES(?,?)",
                enumerate(paths),
            )
            list_touch_revision(db, table)
    return len(paths)


def list_last_search_replace0(db: sqlite3.Connection, raw: bytes) -> int:
    """Create the app-owned last-search list on first use, then replace it atomically."""
    list_registry_ensure(db)
    actual = list_table_names(db).get(LAST_SEARCH_TABLE.casefold())
    if actual is None:
        stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with db:
            db.execute(
                f"CREATE TABLE {quote_identifier(LAST_SEARCH_TABLE)} "
                "(position INTEGER PRIMARY KEY, path TEXT NOT NULL)"
            )
            db.execute(
                f"INSERT INTO {quote_identifier(LIST_REGISTRY)} "
                "(table_name,source_file,source_sha256,entry_count,migrated_at,revision) "
                "VALUES(?,?,?,?,?,0)",
                (LAST_SEARCH_TABLE, LAST_SEARCH_SOURCE, "", 0, stamp),
            )
    else:
        row = db.execute(
            f"SELECT source_file FROM {quote_identifier(LIST_REGISTRY)} "
            "WHERE table_name=? COLLATE NOCASE",
            (actual,),
        ).fetchone()
        if not row or row[0] != LAST_SEARCH_SOURCE:
            raise ValueError(
                f"o nome reservado {LAST_SEARCH_TABLE!r} já pertence a outra lista/tabela"
            )
        list_table_validate(db, actual)
    return list_replace0(db, LAST_SEARCH_TABLE, raw)


def list_clear(db: sqlite3.Connection, table: str) -> int:
    table = list_registered(db, table)
    quoted = quote_identifier(table)
    with db:
        removed = db.execute(f"SELECT count(*) FROM {quoted}").fetchone()[0]
        if removed:
            db.execute(f"DELETE FROM {quoted}")
            list_touch_revision(db, table)
    return removed


def list_menu0(db: sqlite3.Connection) -> None:
    rows = db.execute(
        f"SELECT table_name,entry_count FROM {quote_identifier(LIST_REGISTRY)} "
        "ORDER BY CASE table_name WHEN 'temp_playlist_1' THEN 1 "
        "WHEN 'temp_playlist_2' THEN 2 WHEN 'temp_playlist_3' THEN 3 ELSE 4 END, "
        "table_name COLLATE NOCASE"
    )
    for table, count in rows:
        list_table_validate(db, table)
        current = db.execute(f"SELECT count(*) FROM {quote_identifier(table)}").fetchone()[0]
        sys.stdout.buffer.write(table.encode("utf-8", "surrogateescape") + b"\0")
        sys.stdout.buffer.write(str(current).encode("ascii") + b"\0")


def list_export(db: sqlite3.Connection, table: str) -> None:
    table = list_registered(db, table)
    for (path,) in db.execute(
        f"SELECT path FROM {quote_identifier(table)} ORDER BY position"
    ):
        sys.stdout.buffer.write(path.encode("utf-8", "surrogateescape") + b"\n")


def list_export0(db: sqlite3.Connection, table: str) -> None:
    table = list_registered(db, table)
    for (path,) in db.execute(
        f"SELECT path FROM {quote_identifier(table)} ORDER BY position"
    ):
        sys.stdout.buffer.write(path.encode("utf-8", "surrogateescape") + b"\0")


def main():
    ap = argparse.ArgumentParser(description="eazy incremental SQLite index")
    ap.add_argument("--db", required=True)
    ap.add_argument("--scan0", action="store_true", help="read NUL-separated paths from stdin")
    ap.add_argument("--scan-tree", metavar="PATH", help="incrementally scan a tree using per-directory MD5 signatures")
    ap.add_argument("--sync-dir", metavar="PATH", help="check and incrementally sync one directory")
    ap.add_argument("--watch-covered-root", default="", help="active watcher root covering --sync-dir; allows a guarded MD5 skip")
    ap.add_argument("--watch-queue-dir", default="", help="watcher event queue; any pending .evt disables the guarded skip")
    ap.add_argument("--progress-file", metavar="PATH", help="write compact scan progress state")
    ap.add_argument("--total-count", type=int, default=0, help="known total paths for progress reporting")
    ap.add_argument("--exclude-path", default="", help="exclude this path and its descendants from scans/queries")
    ap.add_argument("--query", action="store_true", help="query indexed files")
    ap.add_argument("--root", default="", help="query root")
    ap.add_argument("--roots-file", default="", help="NUL-separated query roots")
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
    ap.add_argument("--history-record", metavar="PATH", help="registra caminho reproduzido no histórico SQLite")
    ap.add_argument("--history-remove", metavar="PATH", help="remove somente o caminho da tabela de histórico")
    ap.add_argument("--history-remove0", action="store_true", help="remove caminhos NUL-delimitados de history_items")
    ap.add_argument("--history-clear", action="store_true", help="remove todos os registros de history_items")
    ap.add_argument("--list-init", action="store_true", help="inicializa/valida tabelas de listas sem importar arquivos")
    ap.add_argument("--legacy-dir", default="", help="pasta usada para detectar arquivos de listas ainda não migrados")
    ap.add_argument("--list-menu0", action="store_true", help="emite nome e contagem de cada lista separados por NUL")
    ap.add_argument("--list-count", metavar="TABLE", help="conta os itens de uma lista")
    ap.add_argument("--list-export", metavar="TABLE", help="emite os caminhos da lista, em ordem, uma linha por item")
    ap.add_argument("--list-export0", metavar="TABLE", help="emite os caminhos da lista em ordem, separados por NUL")
    ap.add_argument("--list-create", metavar="TABLE", help="cria uma lista temporária SQL vazia")
    ap.add_argument("--list-append0", metavar="TABLE", help="anexa caminhos NUL-delimitados sem duplicar caminhos existentes")
    ap.add_argument("--list-remove0", metavar="TABLE", help="remove todos os caminhos NUL-delimitados da lista")
    ap.add_argument("--list-replace0", metavar="TABLE", help="substitui a lista pelo fluxo NUL-delimitado, preservando ordem e duplicatas")
    ap.add_argument("--list-last-search-replace0", action="store_true", help="cria/substitui a tabela interna Última pesquisa")
    ap.add_argument("--list-clear", metavar="TABLE", help="esvazia uma lista sem remover sua tabela")
    ap.add_argument("--selection-toggle-local", metavar="PATH", help="alterna selected entre 0 e 1")
    ap.add_argument("--selection-toggle-ui", metavar="PATH", help="alterna seleção e retorna estatísticas atualizadas da interface")
    ap.add_argument("--selection-toggle-directory-ui", metavar="PATH", help="alterna uma pasta e seus arquivos NUL de stdin, retornando estatísticas")
    ap.add_argument("--selection-set", nargs=2, metavar=("PATH", "STATE"), help="define selected como 0, 1 ou 2")
    ap.add_argument("--selection-set0", metavar="STATE", help="define estado em lote para caminhos NUL no stdin")
    ap.add_argument("--selection-invert0", action="store_true", help="inverte seleção global em lote para caminhos NUL no stdin")
    ap.add_argument("--selection-toggle-all0", action="store_true", help="alterna lote visível entre selected=1 e 0")
    ap.add_argument("--selection-promote", action="store_true", help="converte selected=1 em selected=2")
    ap.add_argument("--selection-root", default="", help="limita operação de seleção a uma pasta")
    ap.add_argument("--selection-clear", action="store_true", help="limpa marcas selected")
    ap.add_argument("--selection-import-file", metavar="PATH", help="importa selected_paths legado uma única vez sem alterá-lo")
    ap.add_argument("--selection-state", type=int, choices=(1, 2), help="estado-alvo para limpar ou listar")
    ap.add_argument("--selection-list0", action="store_true", help="emite caminhos selecionados separados por NUL")
    ap.add_argument("--selection-roots0", action="store_true", help="emite diretórios globalmente selecionados separados por NUL")
    ap.add_argument("--selection-local-view0", action="store_true", help="emite estado e caminho NUL para a seleção imediata/local da pasta")
    ap.add_argument("--selection-count", action="store_true", help="conta seleção diretamente no SQLite")
    ap.add_argument("--selection-stats", action="store_true", help="retorna itens, bytes e diretórios selecionados")
    ap.add_argument("--selection-ui-stats", action="store_true", help="retorna estatísticas globais e da pasta atual para o cabeçalho")
    ap.add_argument("--dup-session", default="default", help="id efêmero da sessão de seleção de duplicados")
    ap.add_argument("--dup-marks-set0", choices=("selected", "fixed"), help="substitui marcas de duplicados a partir de caminhos NUL no stdin")
    ap.add_argument("--dup-marks-invert0", action="store_true", help="inverte seleção ativa de duplicados para caminhos NUL no stdin")
    ap.add_argument("--dup-marks-toggle", metavar="PATH", help="alterna seleção ativa de um duplicado")
    ap.add_argument("--dup-marks-clear", choices=("selected", "fixed", "all"), help="limpa marcas de duplicados")
    ap.add_argument("--dup-marks-copy-fixed", action="store_true", help="adiciona amostras F12 à seleção ativa")
    ap.add_argument("--dup-marks-list0", choices=("selected", "fixed"), help="lista caminhos marcados separados por NUL")
    ap.add_argument("--dup-marks-stats", action="store_true", help="conta itens e bytes marcados em Duplicados")
    ap.add_argument("--dup-results-init", nargs="?", const="", metavar="LEGACY_PATH", help="inicializa resultados e importa temp_duplicados uma única vez se a tabela ainda não existir")
    ap.add_argument("--dup-results-replace", metavar="LEGACY_TSV_PATH", help="substitui resultados a partir de TSV legado")
    ap.add_argument("--dup-results-export", action="store_true", help="emite resultados em TSV compatível")
    ap.add_argument("--dup-results-count", action="store_true", help="conta resultados persistidos")
    ap.add_argument("--dup-results-clear", action="store_true", help="remove todos os resultados persistidos")
    ap.add_argument("--dup-results-remove", metavar="PATH", help="remove linhas com este caminho dos resultados")
    ap.add_argument("--init", action="store_true")
    args = ap.parse_args()
    write_mode = bool(
        args.init or args.scan0 or args.scan_tree or args.sync_dir or args.history_sync0 or args.history_sync_file or args.history_record or args.history_remove or args.history_remove0 or args.history_clear
        or args.list_init or args.list_create or args.list_append0 or args.list_remove0
        or args.list_replace0 or args.list_last_search_replace0 or args.list_clear
        or args.selection_toggle_local or args.selection_toggle_ui or args.selection_toggle_directory_ui
        or args.selection_set or args.selection_set0 is not None or args.selection_invert0 or args.selection_toggle_all0 or args.selection_promote or args.selection_clear or args.selection_import_file
        or args.dup_marks_set0 or args.dup_marks_invert0 or args.dup_marks_toggle or args.dup_marks_clear or args.dup_marks_copy_fixed
        or args.dup_results_init is not None or args.dup_results_replace or args.dup_results_clear or args.dup_results_remove
    )
    if write_mode:
        db = db_open(args.db)
    else:
        if not Path(args.db).is_file():
            return 2 if (args.query or args.list_menu0 or args.list_count or args.list_export or args.list_export0 or args.selection_list0 or args.selection_roots0 or args.selection_local_view0 or args.selection_count or args.selection_stats or args.selection_ui_stats or args.dup_marks_list0 or args.dup_marks_stats or args.dup_results_export or args.dup_results_count) else 0
        db = db_readonly(args.db)
    if args.init:
        db.close()
        return 0
    if args.dup_results_init is not None:
        try:
            duplicate_results_init(db, args.dup_results_init)
        except (sqlite3.DatabaseError, OSError, ValueError) as exc:
            print(f"Erro ao inicializar resultados de duplicados SQLite: {exc}", file=sys.stderr)
            db.close()
            return 1
        db.close()
        return 0
    if args.dup_results_replace:
        try:
            print(duplicate_results_import(db, args.dup_results_replace))
        except (sqlite3.DatabaseError, OSError, ValueError) as exc:
            print(f"Erro ao importar resultados de duplicados SQLite: {exc}", file=sys.stderr)
            db.close()
            return 1
        db.close()
        return 0
    if args.dup_results_clear or args.dup_results_remove:
        try:
            changed = (duplicate_results_clear(db) if args.dup_results_clear
                       else duplicate_results_remove(db, args.dup_results_remove))
            print(changed)
        except sqlite3.DatabaseError as exc:
            print(f"Erro ao alterar resultados de duplicados SQLite: {exc}", file=sys.stderr)
            db.close()
            return 1
        db.close()
        return 0
    if args.dup_results_count:
        try:
            count = db.execute("SELECT count(*) FROM eazy_duplicate_results").fetchone()[0] if db.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='eazy_duplicate_results'"
            ).fetchone() else 0
            print(count)
        except sqlite3.DatabaseError as exc:
            print(f"Erro ao contar resultados de duplicados SQLite: {exc}", file=sys.stderr)
            db.close()
            return 1
        db.close()
        return 0
    if args.dup_results_export:
        try:
            duplicate_results_export(db)
        except sqlite3.DatabaseError as exc:
            print(f"Erro ao exportar resultados de duplicados SQLite: {exc}", file=sys.stderr)
            db.close()
            return 1
        db.close()
        return 0
    if args.list_init:
        try:
            list_initialize(db, args.legacy_dir)
        except (sqlite3.DatabaseError, OSError, ValueError) as exc:
            print(f"Erro ao inicializar listas SQLite: {exc}", file=sys.stderr)
            db.close()
            return 1
        db.close()
        return 0
    if args.list_create:
        try:
            list_create(db, args.list_create)
        except (sqlite3.DatabaseError, ValueError) as exc:
            print(f"Erro ao criar lista SQLite: {exc}", file=sys.stderr)
            db.close()
            return 1
        db.close()
        return 0
    if args.list_last_search_replace0:
        raw = sys.stdin.buffer.read()
        try:
            changed = list_last_search_replace0(db, raw)
        except (sqlite3.DatabaseError, ValueError) as exc:
            print(f"Erro ao salvar Última pesquisa no SQLite: {exc}", file=sys.stderr)
            db.close()
            return 1
        print(changed)
        db.close()
        return 0
    if args.list_append0 or args.list_remove0 or args.list_replace0:
        table = args.list_append0 or args.list_remove0 or args.list_replace0
        raw = sys.stdin.buffer.read()
        try:
            if args.list_append0:
                changed = list_append0(db, table, raw)
            elif args.list_remove0:
                changed = list_remove0(db, table, raw)
            else:
                changed = list_replace0(db, table, raw)
        except (sqlite3.DatabaseError, ValueError) as exc:
            print(f"Erro ao alterar lista SQLite: {exc}", file=sys.stderr)
            db.close()
            return 1
        print(changed)
        db.close()
        return 0
    if args.list_clear:
        try:
            changed = list_clear(db, args.list_clear)
        except (sqlite3.DatabaseError, ValueError) as exc:
            print(f"Erro ao limpar lista SQLite: {exc}", file=sys.stderr)
            db.close()
            return 1
        print(changed)
        db.close()
        return 0
    if args.list_menu0:
        try:
            list_menu0(db)
        except (sqlite3.DatabaseError, ValueError) as exc:
            print(f"Erro ao listar tabelas SQLite: {exc}", file=sys.stderr)
            db.close()
            return 1
        db.close()
        return 0
    if args.selection_toggle_ui or args.selection_toggle_directory_ui:
        try:
            path = args.selection_toggle_ui or args.selection_toggle_directory_ui
            descendants = (sys.stdin.buffer.read()
                           if args.selection_toggle_directory_ui else b"")
            state, stats = selection_toggle_ui(db, path, args.selection_root, descendants)
            print("\t".join(map(str, (state, *stats))))
        except (sqlite3.DatabaseError, OSError, ValueError) as exc:
            print(f"Erro ao alternar seleção SQLite: {exc}", file=sys.stderr)
            db.close()
            return 1
        db.close()
        return 0
    if args.selection_toggle_local or args.selection_set or args.selection_set0 is not None or args.selection_invert0 or args.selection_toggle_all0 or args.selection_promote or args.selection_clear or args.selection_import_file:
        try:
            if args.selection_toggle_local:
                print(selection_toggle_local(db, args.selection_toggle_local))
            elif args.selection_set:
                path, raw_state = args.selection_set
                print(selection_set(db, path, int(raw_state)))
            elif args.selection_set0 is not None:
                state = int(args.selection_set0)
                if state not in (0, 1, 2):
                    raise ValueError("selected precisa ser 0, 1 ou 2")
                paths = list(dict.fromkeys(item.decode("utf-8", "surrogateescape") for item in sys.stdin.buffer.read().split(b"\0") if item))
                with db:
                    for path in paths:
                        try:
                            path = selection_ensure_path(db, path)
                        except OSError:
                            continue
                        db.execute("UPDATE files SET selected=? WHERE path=?", (state, path))
                print(len(paths))
            elif args.selection_invert0:
                print(selection_invert0(db, sys.stdin.buffer.read()))
            elif args.selection_toggle_all0:
                print(selection_toggle_all0(db, sys.stdin.buffer.read()))
            elif args.selection_promote:
                print(selection_promote(db, args.selection_root))
            elif args.selection_import_file:
                print(selection_import_file(db, args.selection_import_file))
            else:
                print(selection_clear(db, args.selection_state, args.selection_root))
        except (sqlite3.DatabaseError, OSError, ValueError) as exc:
            print(f"Erro ao alterar seleção SQLite: {exc}", file=sys.stderr)
            db.close()
            return 1
        db.close()
        return 0
    if args.dup_marks_set0 or args.dup_marks_invert0 or args.dup_marks_toggle or args.dup_marks_clear or args.dup_marks_copy_fixed:
        try:
            if args.dup_marks_set0:
                result = duplicate_marks_set0(db, args.dup_session, args.dup_marks_set0, sys.stdin.buffer.read())
            elif args.dup_marks_invert0:
                result = duplicate_marks_invert0(db, args.dup_session, sys.stdin.buffer.read())
            elif args.dup_marks_toggle:
                result = duplicate_marks_toggle(db, args.dup_session, args.dup_marks_toggle)
            elif args.dup_marks_copy_fixed:
                result = duplicate_marks_copy_fixed(db, args.dup_session)
            else:
                result = duplicate_marks_clear(db, args.dup_session, args.dup_marks_clear)
            print(result)
        except (sqlite3.DatabaseError, OSError, ValueError) as exc:
            print(f"Erro ao alterar marcas de duplicados SQLite: {exc}", file=sys.stderr)
            db.close()
            return 1
        db.close()
        return 0
    if args.dup_marks_list0:
        try:
            duplicate_marks_list0(db, args.dup_session, args.dup_marks_list0)
        except (sqlite3.DatabaseError, ValueError) as exc:
            print(f"Erro ao consultar marcas de duplicados SQLite: {exc}", file=sys.stderr)
            db.close()
            return 1
        db.close()
        return 0
    if args.dup_marks_stats:
        try:
            count, size = duplicate_marks_stats(db, args.dup_session)
            print(f"{count}\t{size}")
        except sqlite3.DatabaseError as exc:
            print(f"Erro ao consultar estatísticas de Duplicados SQLite: {exc}", file=sys.stderr)
            db.close()
            return 1
        db.close()
        return 0
    if args.selection_local_view0:
        try:
            exact = os.path.abspath(args.selection_root).rstrip(os.sep)
            for state, path in db.execute(
                "SELECT selected,path FROM files WHERE selected IN (1,2) AND (parent=? OR path=?) "
                "ORDER BY parent COLLATE NOCASE,name COLLATE NOCASE", (exact, exact)
            ):
                sys.stdout.buffer.write(str(state).encode("ascii") + b"\0")
                sys.stdout.buffer.write(path.encode("utf-8", "surrogateescape") + b"\0")
        except sqlite3.DatabaseError as exc:
            print(f"Erro ao consultar marcas locais SQLite: {exc}", file=sys.stderr)
            db.close()
            return 1
        db.close()
        return 0
    if args.selection_roots0:
        try:
            for (path,) in db.execute(
                "SELECT path FROM files WHERE kind='directory' AND selected=2 AND deleted=0 ORDER BY length(path),path COLLATE NOCASE"
            ):
                sys.stdout.buffer.write(path.encode("utf-8", "surrogateescape") + b"\0")
        except sqlite3.DatabaseError as exc:
            print(f"Erro ao consultar pastas selecionadas SQLite: {exc}", file=sys.stderr)
            db.close()
            return 1
        db.close()
        return 0
    if args.selection_ui_stats:
        try:
            print("\t".join(map(str, selection_ui_stats(db, args.selection_root))))
        except sqlite3.DatabaseError as exc:
            print(f"Erro ao consultar estatísticas de UI da seleção SQLite: {exc}", file=sys.stderr)
            db.close()
            return 1
        db.close()
        return 0
    if args.selection_stats:
        try:
            count, size, dirs = selection_stats(db, args.selection_state)
            print(f"{count}\t{size}\t{dirs}")
        except sqlite3.DatabaseError as exc:
            print(f"Erro ao consultar estatísticas da seleção SQLite: {exc}", file=sys.stderr)
            db.close()
            return 1
        db.close()
        return 0
    if args.selection_count:
        try:
            print(selection_count(db, args.selection_state))
        except sqlite3.DatabaseError as exc:
            print(f"Erro ao contar seleção SQLite: {exc}", file=sys.stderr)
            db.close()
            return 1
        db.close()
        return 0
    if args.selection_list0:
        try:
            sql = "SELECT path FROM files WHERE selected<>0"
            params: list[object] = []
            if args.selection_state is not None:
                sql += " AND selected=?"
                params.append(args.selection_state)
            if args.selection_root:
                exact = os.path.abspath(args.selection_root).rstrip(os.sep)
                root = exact + os.sep
                sql += " AND (path=? OR substr(path,1,?)=?)"
                params.extend([exact, len(root), root])
            sql += " ORDER BY parent COLLATE NOCASE,name COLLATE NOCASE"
            for (path,) in db.execute(sql, params):
                sys.stdout.buffer.write(path.encode("utf-8", "surrogateescape") + b"\0")
        except sqlite3.DatabaseError as exc:
            print(f"Erro ao consultar seleção SQLite: {exc}", file=sys.stderr)
            db.close()
            return 1
        db.close()
        return 0
    if args.list_count or args.list_export or args.list_export0:
        table = args.list_count or args.list_export or args.list_export0
        try:
            table = list_registered(db, table)
            if args.list_count:
                print(db.execute(f"SELECT count(*) FROM {quote_identifier(table)}").fetchone()[0])
            elif args.list_export0:
                list_export0(db, table)
            else:
                list_export(db, table)
        except (sqlite3.DatabaseError, ValueError) as exc:
            print(f"Erro ao consultar lista SQLite: {exc}", file=sys.stderr)
            db.close()
            return 1
        db.close()
        return 0
    if args.scan_tree:
        try:
            scan_tree(db, args.scan_tree, progress_file=args.progress_file,
                      exclude_path=args.exclude_path)
        except (OSError, sqlite3.DatabaseError, ValueError) as exc:
            print(f"Erro ao atualizar a árvore SQLite: {exc}", file=sys.stderr)
            db.close()
            return 1
        db.close()
        return 0
    if args.sync_dir:
        try:
            result = sync_directory(db, args.sync_dir, exclude_path=args.exclude_path,
                                    watch_root=args.watch_covered_root,
                                    watch_queue_dir=args.watch_queue_dir)
        except OSError as exc:
            print(f"Erro ao sincronizar pasta: {exc}", file=sys.stderr)
            db.close()
            return 1
        print("SYNC\t{changed}\t{removed}\t{revived}\t{files}\t{bytes}".format(**result))
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
    if args.history_record:
        try:
            with db:
                db.execute("CREATE TABLE IF NOT EXISTS history_state (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
                db.execute("UPDATE history_items SET position=position+1")
                db.execute("DELETE FROM history_items WHERE path=?", (args.history_record,))
                db.execute(
                    "INSERT INTO history_items(path, position, played_at) VALUES (?, 0, ?)",
                    (args.history_record, int(time.time())),
                )
                db.execute("DELETE FROM history_items WHERE position>=200")
        except sqlite3.DatabaseError as exc:
            print(f"Erro ao registrar histórico: {exc}", file=sys.stderr)
            db.close()
            return 1
        db.close()
        return 0
    if args.history_remove:
        try:
            with db:
                db.execute("DELETE FROM history_items WHERE path=?", (args.history_remove,))
        except sqlite3.DatabaseError as exc:
            print(f"Erro ao remover do histórico: {exc}", file=sys.stderr)
            db.close()
            return 1
        db.close()
        return 0
    if args.history_remove0:
        paths = [p.decode("utf-8", "surrogateescape") for p in sys.stdin.buffer.read().split(b"\0") if p]
        try:
            with db:
                before = db.total_changes
                db.executemany("DELETE FROM history_items WHERE path=?", ((p,) for p in paths))
                removed = db.total_changes - before
        except sqlite3.DatabaseError as exc:
            print(f"Erro ao remover registros do histórico: {exc}", file=sys.stderr)
            db.close()
            return 1
        print(removed)
        db.close()
        return 0
    if args.history_clear:
        try:
            with db:
                db.execute("CREATE TABLE IF NOT EXISTS history_state (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
                cur = db.execute("DELETE FROM history_items")
                removed = cur.rowcount
                db.execute("INSERT OR REPLACE INTO history_state(key, value) VALUES ('migrated', '1')")
        except sqlite3.DatabaseError as exc:
            print(f"Erro ao limpar histórico: {exc}", file=sys.stderr)
            db.close()
            return 1
        print(max(removed, 0))
        db.close()
        return 0
    if args.history_list:
        for (path,) in db.execute("SELECT path FROM history_items ORDER BY position ASC, id ASC"):
            print(path)
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
            print(f"{size}\t{mtime_ns // 1_000_000_000}\t{output_kind}\t{name}\t{path}\t{duration_ms or ''}\t{ext}")
        db.close()
        return 0
    if args.lookup0:
        paths = [p.decode("utf-8", "surrogateescape") for p in sys.stdin.buffer.read().split(b"\0") if p]
        # Mantém margem sob o limite de variáveis SQL, inclusive em listas longas.
        for start in range(0, len(paths), 500):
            batch = paths[start:start + 500]
            marks = ",".join("?" for _ in batch)
            rows = db.execute(
                f"SELECT size,mtime_ns,kind,name,path,duration_ms,extension,deleted FROM files WHERE path IN ({marks})",
                batch,
            ).fetchall()
            for size, mtime_ns, kind, name, path, duration_ms, ext, deleted in rows:
                output_kind = "d" if kind == "directory" else "f"
                if deleted:
                    output_kind = "x" if output_kind == "f" else "X"
                print(f"{size}\t{mtime_ns // 1_000_000_000}\t{output_kind}\t{name}\t{path}\t{duration_ms or ''}\t{ext}")
        db.close()
        return 0
    if args.scan0:
        scan(db, iter_nul_paths(sys.stdin.buffer), progress_file=args.progress_file,
             quiet=bool(args.progress_file), exclude_path=args.exclude_path,
             total_count=args.total_count)
    elif args.query:
        if args.roots_file:
            raw_roots = Path(args.roots_file).read_bytes().split(b"\0")
            roots = [os.path.abspath(p.decode("utf-8", "surrogateescape")) for p in raw_roots if p]
        else:
            roots = [os.path.abspath(args.root or os.getcwd())]
        roots = list(dict.fromkeys(r.rstrip(os.sep) or os.sep for r in roots))
        if not roots:
            roots = [os.path.abspath(args.root or os.getcwd()).rstrip(os.sep) or os.sep]

        def scope_predicate(query_roots: list[str], column: str = "path") -> tuple[str, list[object]]:
            clauses: list[str] = []
            values: list[object] = []
            for query_root in query_roots:
                prefix = query_root.rstrip(os.sep) + os.sep if query_root != os.sep else os.sep
                clauses.append(f"({column}=? OR substr({column},1,?)=?)")
                values.extend([query_root, len(prefix), prefix])
            return "(" + " OR ".join(clauses) + ")", values

        root_where, root_params = scope_predicate(roots)
        excluded = os.path.realpath(args.exclude_path) if args.exclude_path else ""
        excluded_prefix = excluded.rstrip(os.sep) + os.sep if excluded and excluded != os.sep else os.sep
        for query_root in roots:
            one_root_where, one_root_params = scope_predicate([query_root])
            check_where = one_root_where
            check_params = list(one_root_params)
            if excluded:
                check_where += " AND path<>? AND substr(path,1,?)<>?"
                check_params.extend([excluded, len(excluded_prefix), excluded_prefix])
            indexed = db.execute(f"SELECT count(*) FROM files WHERE {check_where}", check_params).fetchone()[0]
            if indexed == 0:
                db.close()
                return 2

        extensions: set[str] = set()
        name_patterns: list[str] = []
        for token in args.ext.split():
            if not token:
                continue
            if token.upper() == "TODAS":
                extensions.clear()
                name_patterns.clear()
                break
            if token.startswith(".") and not any(ch in token for ch in "*?["):
                extensions.add(token.lstrip(".").lower())
            elif any(ch in token for ch in "*?[") or "." in token:
                name_patterns.append(token)
            else:
                extensions.add(token.lower().lstrip("."))

        sql = "SELECT size, mtime_ns, kind, name, path, duration_ms, extension, deleted FROM files WHERE "
        if args.include_dirs:
            sql += "1=1"
        else:
            sql += "kind != 'directory'"
        if args.direct:
            marks = ",".join("?" for _ in roots)
            sql += f" AND parent IN ({marks})"
            params = list(roots)
        else:
            sql += f" AND {root_where}"
            params = list(root_params)
        if excluded:
            sql += " AND path<>? AND substr(path,1,?)<>?"
            params.extend([excluded, len(excluded_prefix), excluded_prefix])
        if not args.show_deleted:
            sql += " AND deleted=0"
        if extensions or name_patterns:
            type_clauses: list[str] = []
            if extensions:
                marks = ",".join("?" for _ in extensions)
                type_clauses.append(f"lower(ltrim(extension, '.')) IN ({marks})")
                params.extend(sorted(extensions))
            for pattern in name_patterns:
                type_clauses.append("lower(name) GLOB lower(?)")
                params.append(pattern)
            sql += " AND (kind='directory' OR (" + " OR ".join(type_clauses) + "))"
        if args.min_size:
            sql += " AND size > ?"
            params.append(args.min_size)
        if args.max_size:
            sql += " AND size < ?"
            params.append(args.max_size)
        # Diretórios ficam sempre no topo. Para diretórios, `size` é somente
        # o st_size da própria entrada; nunca somamos a árvore.
        sql += " ORDER BY CASE WHEN kind='directory' THEN 0 ELSE 1 END, "
        if args.max_size or args.min_size:
            sql += "size DESC, "
        sql += "name COLLATE NOCASE"
        for size, mtime_ns, kind, name, path, duration_ms, _ext, deleted in db.execute(sql, params):
            output_kind = "d" if kind == "directory" else "f"
            if deleted:
                output_kind = "x" if output_kind == "f" else "X"
            print(f"{size}\t{mtime_ns // 1_000_000_000}\t{output_kind}\t{name}\t{path}\t{duration_ms or ''}")
    db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

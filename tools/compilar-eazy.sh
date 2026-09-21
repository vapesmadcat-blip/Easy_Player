#!/usr/bin/env bash
set -euo pipefail

SRC="${1:-eazy}"
OUT="${2:-eazy-linux-x86_64}"

if [[ ! -f "$SRC" ]]; then
  echo "Uso: $0 ARQUIVO_EAZY [EXECUTAVEL_SAIDA]" >&2
  echo "Exemplo: $0 eazy eazy-linux-x86_64" >&2
  exit 2
fi

command -v python3 >/dev/null || { echo "Erro: instale python3." >&2; exit 1; }
command -v gcc >/dev/null || { echo "Erro: instale gcc: sudo apt install build-essential" >&2; exit 1; }
[[ -f /usr/include/zlib.h ]] || { echo "Erro: instale zlib1g-dev: sudo apt install zlib1g-dev" >&2; exit 1; }

SRC_ABS="$(readlink -f -- "$SRC")"
OUT_ABS="$(readlink -m -- "$OUT")"
WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT

python3 - "$SRC_ABS" "$WORKDIR/eazy_wrapper.c" <<'PY'
import sys
import zlib
from pathlib import Path

src = Path(sys.argv[1]).read_bytes()
out = Path(sys.argv[2])
payload = zlib.compress(src, level=9)
array = ','.join(str(b) for b in payload)

c = f'''#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <unistd.h>
#include <zlib.h>

static const unsigned char payload[] = {{{array}}};
static const size_t payload_len = sizeof(payload);
static const size_t script_len = {len(src)};

int main(int argc, char **argv) {{
    unsigned char *script = malloc(script_len);
    if (!script) {{ perror("eazy: malloc"); return 1; }}
    uLongf out_len = (uLongf)script_len;
    if (uncompress(script, &out_len, payload, (uLong)payload_len) != Z_OK || out_len != script_len) {{
        fprintf(stderr, "eazy: falha ao preparar o script\\n");
        free(script);
        return 1;
    }}
    char path[] = "/tmp/.eazy-script-XXXXXX";
    int fd = mkstemp(path);
    if (fd < 0) {{ perror("eazy: mkstemp"); free(script); return 1; }}
    if (fchmod(fd, 0700) < 0) {{ perror("eazy: chmod"); close(fd); unlink(path); free(script); return 1; }}
    size_t off = 0;
    while (off < script_len) {{
        ssize_t n = write(fd, script + off, script_len - off);
        if (n < 0) {{
            if (errno == EINTR) continue;
            perror("eazy: write");
            close(fd); unlink(path); free(script); return 1;
        }}
        off += (size_t)n;
    }}
    free(script);
    close(fd);
    char **args = calloc((size_t)argc + 2, sizeof(char *));
    if (!args) {{ perror("eazy: calloc"); unlink(path); return 1; }}
    args[0] = "/bin/bash";
    args[1] = path;
    for (int i = 1; i < argc; ++i) args[i + 1] = argv[i];
    args[argc + 1] = NULL;
    execv("/bin/bash", args);
    perror("eazy: exec /bin/bash");
    unlink(path);
    return 127;
}}
'''
out.write_text(c)
PY

gcc -O2 -s -o "$OUT_ABS" "$WORKDIR/eazy_wrapper.c" -lz
chmod 755 "$OUT_ABS"

echo "Executável criado: $OUT_ABS"
file "$OUT_ABS"
ls -lh "$OUT_ABS"
sha256sum "$OUT_ABS"

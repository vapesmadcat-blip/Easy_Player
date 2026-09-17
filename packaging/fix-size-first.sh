#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
VERSION="3.3.7"
python3 - "$ROOT" "$VERSION" <<'PY'
from pathlib import Path
import sys
root=Path(sys.argv[1]); version=sys.argv[2]

p=root/'eazy'
s=p.read_text().replace('EAZY_VERSION="3.3.6"', f'EAZY_VERSION="{version}"', 1)
s=s.replace('''        # info: data · tamanho · tipo/ext
        if (tipo == "d") {
            info = sprintf("%s · %s", dt, tipo_lab)
        } else {
            info = sprintf("%s · %sMB · .%s", dt, mb, tipo_lab)
        }''','''        # info: TAM · data · tipo/ext (tamanho primeiro para leitura rápida)
        if (tipo == "d") {
            info = sprintf("-- MB · %s · %s", dt, tipo_lab)
        } else {
            info = sprintf("%sMB · %s · .%s", mb, dt, tipo_lab)
        }''',1)
p.write_text(s)

p=root/'eazy.1'
s=p.read_text().replace('eazy 3.3.6', f'eazy {version}')
p.write_text(s)

p=root/'packaging/eazy/debian/control'
s=p.read_text().replace('Version: 3.3.6', f'Version: {version}')
p.write_text(s)

p=root/'packaging/eazy/debian/changelog'
p.write_text(f'''eazy ({version}) unstable; urgency=medium\n\n  * Display file size before date and type in the main browser and search lists.\n\n -- eazy contributors <vapesmadcat-blip@users.noreply.github.com>  Thu, 17 Sep 2026 19:42:00 +0000\n'''+p.read_text())

p=root/'CHANGELOG.md'
s=p.read_text().replace('# Changelog\n', f'# Changelog\n\n## {version} — tamanho primeiro\n- A lista principal e a busca agora exibem `TAM · data · tipo`, com o tamanho primeiro.\n')
p.write_text(s)

p=root/'README.md'
s=p.read_text().replace('# eazy 3.3.5 (release)', f'# eazy {version} (release)')
p.write_text(s)

p=root/'install-eazy-completo.sh'
s=p.read_text().replace('VERSION="3.3.6"', f'VERSION="{version}"')
p.write_text(s)
PY

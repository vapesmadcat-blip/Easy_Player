#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
VERSION="3.3.9"
python3 - "$ROOT" "$VERSION" <<'PY'
from pathlib import Path
import sys
root=Path(sys.argv[1]); version=sys.argv[2]
p=root/'eazy'
s=p.read_text().replace('EAZY_VERSION="3.3.8"', f'EAZY_VERSION="{version}"', 1)
s=s.replace('''        # A cor representa o tipo do arquivo; não alterna pela posição da linha.
        c_ord = cor
''','''        # Ciclo visual idx3: mantém as três cores de ordenação por posição.
        idx++
        c_ord = (idx % 3 == 1) ? c_ord1 : (idx % 3 == 2) ? c_ord2 : c_ord3
''',1)
s=s.replace('''            chave, cor, icon, nome_exib, c_reset, cor, info, c_reset, caminho''','''            chave, cor, icon, nome_exib, c_reset, c_ord, info, c_reset, caminho''',1)
p.write_text(s)
for name in ['eazy.1','packaging/eazy/debian/control']:
    p=root/name; p.write_text(p.read_text().replace('3.3.8',version))
p=root/'packaging/eazy/debian/changelog'; p.write_text(f'''eazy ({version}) unstable; urgency=medium\n\n  * Restore the idx3 three-color visual cycle requested for file rows.\n\n -- eazy contributors <vapesmadcat-blip@users.noreply.github.com>  Thu, 17 Sep 2026 19:55:00 +0000\n\n'''+p.read_text())
p=root/'CHANGELOG.md'; p.write_text(p.read_text().replace('# Changelog\n', f'# Changelog\n\n## {version} — idx3 restaurado\n- Restaurado o ciclo visual de três cores por índice nas linhas de arquivos.\n'))
p=root/'README.md'; p.write_text(p.read_text().replace('# eazy 3.3.8 (release)', f'# eazy {version} (release)'))
p=root/'install-eazy-completo.sh'; p.write_text(p.read_text().replace('VERSION="3.3.8"', f'VERSION="{version}"'))
PY

#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
VERSION="3.3.8"
python3 - "$ROOT" "$VERSION" <<'PY'
from pathlib import Path
import sys
root=Path(sys.argv[1]); version=sys.argv[2]
p=root/'eazy'
s=p.read_text().replace('EAZY_VERSION="3.3.7"', f'EAZY_VERSION="{version}"', 1)
s=s.replace('''        chave = (modo == "data") ? int(mtime) : bytes
        # Cor da coluna de índice/ordenação (cicla para identificar ordem)
        idx++
        c_ord = (idx % 3 == 1) ? c_ord1 : (idx % 3 == 2) ? c_ord2 : c_ord3
''','''        chave = (modo == "data") ? int(mtime) : bytes
        # A cor representa o tipo do arquivo; não alterna pela posição da linha.
        c_ord = cor
''',1)
s=s.replace('''            chave, cor, icon, nome_exib, c_reset, c_ord, info, c_reset, caminho''','''            chave, cor, icon, nome_exib, c_reset, cor, info, c_reset, caminho''',1)
p.write_text(s)
p=root/'eazy.1'; p.write_text(p.read_text().replace('eazy 3.3.7', f'eazy {version}'))
p=root/'packaging/eazy/debian/control'; p.write_text(p.read_text().replace('Version: 3.3.7', f'Version: {version}'))
p=root/'packaging/eazy/debian/changelog'; p.write_text(f'''eazy ({version}) unstable; urgency=medium\n\n  * Use consistent colors by file type instead of cycling colors by row.\n\n -- eazy contributors <vapesmadcat-blip@users.noreply.github.com>  Thu, 17 Sep 2026 19:52:00 +0000\n\n'''+p.read_text())
p=root/'CHANGELOG.md'; p.write_text(p.read_text().replace('# Changelog\n', f'# Changelog\n\n## {version} — cores consistentes\n- Vídeos, áudios, imagens, compactados e documentos mantêm uma cor fixa por tipo.\n- Removida a alternância de cores baseada na posição da linha.\n'))
p=root/'README.md'; p.write_text(p.read_text().replace('# eazy 3.3.7 (release)', f'# eazy {version} (release)'))
p=root/'install-eazy-completo.sh'; p.write_text(p.read_text().replace('VERSION="3.3.7"', f'VERSION="{version}"'))
PY

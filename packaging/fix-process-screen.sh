#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
VERSION="3.3.2"

python3 - "$ROOT" "$VERSION" <<'PY'
from pathlib import Path
import sys
root=Path(sys.argv[1]); version=sys.argv[2]

p=root/'eazy'
s=p.read_text()
s=s.replace('EAZY_VERSION="3.3.1"', f'EAZY_VERSION="{version}"', 1)
old='''processos_pesados() {
    {
        echo "10 Processos que mais usam CPU:"
        ps aux --sort=-%cpu 2>/dev/null | head -11 || true
        echo ""
        echo "10 Processos que mais usam memória:"
        ps aux --sort=-%mem 2>/dev/null | head -11 || true
    } | eazy_mostrar_texto "Processos Pesados" 26 90
}'''
new='''processos_pesados() {
    {
        printf '%-10s %7s %6s %6s %8s %6s %8s %s\\n' \\
            USER PID '%CPU' '%MEM' RSS STAT TEMPO COMANDO
        ps -eo user=,pid=,%cpu=,%mem=,rss=,stat=,etime=,comm= --sort=-%cpu 2>/dev/null | \\
            head -n 10 || true
        echo ""
        printf '%-10s %7s %6s %6s %8s %6s %8s %s\\n' \\
            USER PID '%CPU' '%MEM' RSS STAT TEMPO COMANDO
        ps -eo user=,pid=,%cpu=,%mem=,rss=,stat=,etime=,comm= --sort=-%mem 2>/dev/null | \\
            head -n 10 || true
    } | eazy_mostrar_texto "Processos Pesados" 26 88
}'''
if old not in s:
    raise SystemExit('bloco processos_pesados não encontrado')
s=s.replace(old,new,1)
p.write_text(s)

p=root/'eazy.1'
s=p.read_text().replace('"eazy 3.3.1"','"eazy 3.3.2"').replace('"eazy 3.3.1 (IA)"','"eazy 3.3.2 (IA)"')
s=s.replace('eazy_3.3.1_all.deb','eazy_3.3.2_all.deb').replace('eazy-v3.3.1','eazy-v3.3.2').replace('eazy-gnome_3.3.1_all.deb','eazy-gnome_3.3.2_all.deb').replace('eazy-kde_3.3.1_all.deb','eazy-kde_3.3.2_all.deb')
p.write_text(s)

p=root/'README.md'
s=p.read_text().replace('# eazy 3.3.1 (release)', '# eazy 3.3.2 (release)').replace('eazy_3.3.1_all.deb','eazy_3.3.2_all.deb').replace('eazy-gnome_3.3.1_all.deb','eazy-gnome_3.3.2_all.deb').replace('eazy-kde_3.3.1_all.deb','eazy-kde_3.3.2_all.deb')
p.write_text(s)

p=root/'CHANGELOG.md'
s=p.read_text().replace('# Changelog\n', '# Changelog\n\n## 3.3.2 — tela de processos\n- Corrigida a janela “Processos Pesados”: comandos longos não quebram mais a interface.\n- Lista agora usa colunas compactas de usuário, PID, CPU, memória, RSS, estado, tempo e comando.\n')
p.write_text(s)
PY
sed -i 's/^Version: .*/Version: 3.3.2/' "$ROOT/packaging/eazy/debian/control"
cat > "$ROOT/packaging/eazy/debian/changelog" <<'EOF'
eazy (3.3.2) unstable; urgency=medium

  * Fix Processos Pesados dialog by using compact process columns.
  * Prevent long command lines from wrapping and corrupting the textbox view.

 -- eazy contributors <vapesmadcat-blip@users.noreply.github.com>  Thu, 17 Sep 2026 18:32:00 +0000
EOF
sed -i 's/VERSION="3.3.1"/VERSION="3.3.2"/' "$ROOT/packaging/desktop/build-desktop-pkgs.sh"
sed -i 's/3.3.1/3.3.2/g' "$ROOT/packaging/desktop/README.md"
chmod +x "$ROOT/packaging/fix-process-screen.sh"
printf 'Correção preparada para eazy %s\n' "$VERSION"

#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
VERSION="3.6.0"
python3 - "$ROOT" "$VERSION" <<'PY'
from pathlib import Path
import sys
root=Path(sys.argv[1]); version=sys.argv[2]
p=root/'eazy'; s=p.read_text().replace('EAZY_VERSION="3.5.0"', f'EAZY_VERSION="{version}"', 1)
s=s.replace('''PLAYLIST_DIR_PADRAO="${HOME}/Playlists"
PLAYER_PADRAO="mpv"
''','''PLAYLIST_DIR_PADRAO="${HOME}/Playlists"
DOWNLOAD_DIR="${HOME}/Downloads"  # padrão: ~/Downloads
PLAYER_PADRAO="mpv"
''',1)
s=s.replace('''SHELL_CMD="${SHELL_CMD:-bash}"
SEL_GLOBAL_OP''','''SHELL_CMD="${SHELL_CMD:-bash}"
DOWNLOAD_DIR="${DOWNLOAD_DIR:-${HOME}/Downloads}"
SEL_GLOBAL_OP''',1)
s=s.replace('''        "config" "Configurar o eazy"''','''        "config" "Configurar o eazy (inclui destino de downloads)"''',1)
s=s.replace('''    local novo_pl_dir
    novo_pl_dir=$(whiptail --title "Configuração: Pasta Padrão de Playlists"''','''    local novo_download_dir
    novo_download_dir=$(whiptail --title "Configuração: Pasta Padrão de Downloads" \\
        --inputbox "Pasta onde os downloads serão salvos por padrão:\\n(default: $HOME/Downloads)" 11 72 "$DOWNLOAD_DIR" \\
        3>&1 1>&2 2>&3)
    [ -n "$novo_download_dir" ] && DOWNLOAD_DIR="$novo_download_dir"
    DOWNLOAD_DIR="${DOWNLOAD_DIR:-${HOME}/Downloads}"

    local novo_pl_dir
    novo_pl_dir=$(whiptail --title "Configuração: Pasta Padrão de Playlists"''',1)
s=s.replace('''PLAYLIST_DIR_PADRAO="$PLAYLIST_DIR_PADRAO"
PLAYER_PADRAO''','''PLAYLIST_DIR_PADRAO="$PLAYLIST_DIR_PADRAO"
DOWNLOAD_DIR="$DOWNLOAD_DIR"
PLAYER_PADRAO''',1)
s=s.replace('''Player: $PLAYER_PADRAO\\nPython:''','''Downloads: $DOWNLOAD_DIR\\nPlayer: $PLAYER_PADRAO\\nPython:''',1)
s=s.replace('''  --config           Assistente de configuração (player, volume, pastas…)''','''  --config           Assistente de configuração (inclui pasta de downloads)''',1)
s=s.replace('''  Ctrl-B             Downloads (yt-dlp, aria2c, axel, wget)''','''  Ctrl-B             Downloads (destino padrão: $HOME/Downloads)''',1)
s=s.replace('''        nome_esperado=$(obter_nome_do_link "$link_alvo")
        dir_antes=$(pwd)
''','''        nome_esperado=$(obter_nome_do_link "$link_alvo")
        dir_antes=$(pwd)
        download_dir="${DOWNLOAD_DIR:-${HOME}/Downloads}"
        mkdir -p -- "$download_dir" || { echo "Não foi possível criar o destino: $download_dir"; read -p "Pressione Enter para continuar..."; continue; }
''',1)
s=s.replace('''verificar_espaco_disco "$((1024*1024*1024))" "." "Download"''','''verificar_espaco_disco "$((1024*1024*1024))" "$download_dir" "Download"''',1)
s=s.replace('''-o "$out_tpl" "$link_limpo"''','''-o "$download_dir/$out_tpl" "$link_limpo"''')
s=s.replace('''-o "$out_tpl" "$link_alvo"''','''-o "$download_dir/$out_tpl" "$link_alvo"''')
s=s.replace('''--insecure -n 4 -o "$nome_esperado" "$link_alvo"''','''--insecure -n 4 -o "$download_dir/$nome_esperado" "$link_alvo"''')
s=s.replace('''--no-check-certificate -O "$nome_esperado" "$link_alvo"''','''--no-check-certificate -O "$download_dir/$nome_esperado" "$link_alvo"''')
s=s.replace('''find . -maxdepth 1 -type f \\( -iname "*.mp4"''','''find "$download_dir" -maxdepth 1 -type f \\( -iname "*.mp4"''')
s=s.replace('''find . -maxdepth 1 -type f -printf '%T@ %p\\n' ''','''find "$download_dir" -maxdepth 1 -type f -printf '%T@ %p\\n' ''')
s=s.replace('''cut -d' ' -f2- | sed 's|^\\./||')''','''cut -d' ' -f2-''')
s=s.replace('''elif [ -f "$nome_esperado" ]; then
            arquivo_baixado="$nome_esperado"''','''elif [ -f "$download_dir/$nome_esperado" ]; then
            arquivo_baixado="$download_dir/$nome_esperado"''',1)
p.write_text(s)

for name in ['eazy.1','packaging/eazy/debian/control']:
    p=root/name; p.write_text(p.read_text().replace('3.5.0',version))
p=root/'packaging/eazy/debian/changelog'; p.write_text(f'''eazy ({version}) unstable; urgency=medium\n\n  * Add configurable download destination in F9 configuration.\n  * Use ~/Downloads as the default destination instead of the current directory.\n\n -- eazy contributors <vapesmadcat-blip@users.noreply.github.com>  Thu, 17 Sep 2026 21:14:00 +0000\n\n'''+p.read_text())
p=root/'CHANGELOG.md'; p.write_text(p.read_text().replace('# Changelog\n', f'# Changelog\n\n## {version} — destino de downloads configurável\n- Default de downloads: `~/Downloads`.\n- Configuração disponível em **F9 → Configurar → Pasta Padrão de Downloads**.\n- A configuração é salva em `~/.config/eazy/config`; `DOWNLOAD_DIR` também pode ser usado no ambiente.\n'))
p=root/'README.md'; s=p.read_text().replace('# eazy 3.5.0 (release)', f'# eazy {version} (release)'); s += f'''\n\n## Destino dos downloads\n\nO destino padrão é **`~/Downloads`**. Para alterar, use **F9 → Configurar → Pasta Padrão de Downloads**. A escolha fica salva em `~/.config/eazy/config`. Também é possível iniciar com `DOWNLOAD_DIR=/caminho eazy`.\n'''; p.write_text(s)
p=root/'GUIA_RAPIDO.md'; s=p.read_text().replace('# Guia rápido do eazy 3.5.0', f'# Guia rápido do eazy {version}'); s += '''\n\n## Destino dos downloads\n\nPor padrão, downloads feitos pelo Ctrl-B são salvos em `~/Downloads`. Altere em **F9 → Configurar → Pasta Padrão de Downloads**. O eazy cria a pasta automaticamente e mostra o destino ao iniciar o download.\n'''; p.write_text(s)
p=root/'EAZY_EXPLICADO.md'; s=p.read_text().replace('# eazy 3.5.0', f'# eazy {version}',1); s += '''\n\n## Destino configurável dos downloads\n\nO destino padrão dos downloads é `~/Downloads`, evitando que arquivos baixados sejam misturados com a pasta que está sendo navegada. A configuração é feita em F9, fica persistida em `~/.config/eazy/config` na variável `DOWNLOAD_DIR` e pode ser sobrescrita pela variável de ambiente de mesmo nome. O eazy cria o diretório quando necessário e usa o mesmo destino para yt-dlp, aria2c, axel e wget.\n'''; p.write_text(s)
p=root/'install-eazy-completo.sh'; p.write_text(p.read_text().replace('VERSION="3.5.0"', f'VERSION="{version}"'))
PY

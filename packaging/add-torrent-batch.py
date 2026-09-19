from pathlib import Path
root=Path('/home/ubuntu/easy_player_current'); version='3.10.0'
# eazy-tor batch mode
p=root/'eazy-tor'; s=p.read_text()
s=s.replace('SEED_RATIO="1.0"; SEED_TIME="0"; MAX_PEERS="100"; SHOW_FILES=false; USE_TOR=false','SEED_RATIO="1.0"; SEED_TIME="0"; MAX_PEERS="100"; SHOW_FILES=false; USE_TOR=false; LIST_FILE=""; LOG_FILE=""; STOP_ON_ERROR=false')
s=s.replace('''  --tor               Usa torsocks neste download
  -s, --show          Mostra os arquivos do torrent''','''  --tor               Usa torsocks neste download
  -L, --list FILE     Baixa uma lista (1 magnet/.torrent por linha)
  --log FILE          Salva log completo do lote
  --stop-on-error     Para no primeiro erro (padrão: continua)
  -s, --show          Mostra os arquivos do torrent''')
s=s.replace('''    --tor) USE_TOR=true; shift;;
    -s|--show) SHOW_FILES=true; shift;;''','''    --tor) USE_TOR=true; shift;;
    -L|--list) [[ $# -ge 2 ]] || { echo -e "${RED}Falta FILE.${NC}" >&2; exit 2; }; LIST_FILE="$2"; shift 2;;
    --log) [[ $# -ge 2 ]] || { echo -e "${RED}Falta FILE.${NC}" >&2; exit 2; }; LOG_FILE="$2"; shift 2;;
    --stop-on-error) STOP_ON_ERROR=true; shift;;
    -s|--show) SHOW_FILES=true; shift;;''')
s=s.replace('''[[ ${#TARGETS[@]} -gt 0 ]] || { print_help >&2; exit 2; }
command -v aria2c''','''if [ -n "$LIST_FILE" ]; then
  [ -f "$LIST_FILE" ] || { echo -e "${RED}Lista não encontrada: $LIST_FILE${NC}" >&2; exit 1; }
  while IFS= read -r line || [ -n "$line" ]; do
    line="${line#"${line%%[![:space:]]*}"}"; line="${line%"${line##*[![:space:]]}"}"
    [[ -z "$line" || "$line" == \#* ]] && continue
    TARGETS+=("$line")
  done < "$LIST_FILE"
fi
[[ ${#TARGETS[@]} -gt 0 ]] || { print_help >&2; exit 2; }
if [ -n "$LOG_FILE" ]; then
  mkdir -p -- "$(dirname -- "$LOG_FILE")"
  exec > >(tee -a "$LOG_FILE") 2>&1
fi
command -v aria2c''')
old='''for target in "${TARGETS[@]}"; do
  echo -e "${YELLOW}Baixando:${NC} $target"
  "${TOR_PREFIX[@]}" aria2c "${ARIA2_OPTS[@]}" "$target"
done
echo -e "${GREEN}✓ Concluído!${NC}"'''
new='''total=${#TARGETS[@]}; ok=0; failed=0; index=0
for target in "${TARGETS[@]}"; do
  index=$((index+1)); echo -e "${YELLOW}[$index/$total] Baixando:${NC} $target"
  if "${TOR_PREFIX[@]}" aria2c "${ARIA2_OPTS[@]}" "$target"; then
    ok=$((ok+1)); echo -e "${GREEN}✓ Item $index concluído${NC}"
  else
    failed=$((failed+1)); echo -e "${RED}✗ Item $index falhou${NC}"
    $STOP_ON_ERROR && break
  fi
done
echo -e "${GREEN}Resumo: $ok concluído(s), $failed falho(s), $total total${NC}"
[ "$failed" -eq 0 ]'''
if old not in s: raise SystemExit('loop batch não encontrado')
s=s.replace(old,new,1); p.write_text(s)
# eazy CLI: generate list from queued torrent records
p=root/'eazy'; s=p.read_text().replace('EAZY_VERSION="3.9.4"',f'EAZY_VERSION="{version}"',1)
s=s.replace('''  --torrent [OPÇÕES] Encaminha para o downloader separado eazy-tor''','''  --torrent [OPÇÕES] Encaminha para o downloader separado eazy-tor
  --torrent-list [FILE] Cria lista em lote a partir da fila do eazy''')
branch='''elif [ "$1" = "--torrent-list" ]; then
    list_file="${2:-$CONFIG_DIR/torrents.list}"
    mkdir -p "$(dirname -- "$list_file")"
    : > "$list_file"
    if [ -f "$DOWNLOAD_QUEUE" ]; then
        awk -F'|' '$1 == "torrent" && $2 != "" {print $2}' "$DOWNLOAD_QUEUE" | awk '!seen[$0]++' > "$list_file"
    fi
    [ -s "$list_file" ] || printf '# Um magnet ou arquivo .torrent por linha\n' > "$list_file"
    echo "Lista criada: $list_file"
    echo "Edite e execute: eazy-tor --list \"$list_file\""
    exit 0
'''
marker='''elif [ "$1" = "--torrent" ]; then
'''
if branch not in s: s=s.replace(marker,branch+marker,1)
p.write_text(s)
# docs/version
for name in ['eazy.1','README.md','GUIA_RAPIDO.md','EAZY_EXPLICADO.md','install-eazy-completo.sh']:
 p=root/name; p.write_text(p.read_text().replace('3.9.4',version))
p=root/'eazy.1'; s=p.read_text()+f'''\n.SH BATCH TORRENTS\nUse\n.B eazy --torrent-list\npara criar\n.B ~/.config/eazy/torrents.list\ncom os magnets e arquivos .torrent já presentes na fila. Edite o arquivo, uma entrada por linha, e monitore o lote com:\n.nf\neazy-tor --list ~/.config/eazy/torrents.list --log ~/.config/eazy/torrents.log\n.fi\nO lote é sequencial por padrão, continua após falhas e apresenta resumo. Use\n.B --stop-on-error\npara parar no primeiro erro.\n'''; p.write_text(s)
for name in ['README.md','GUIA_RAPIDO.md','EAZY_EXPLICADO.md']:
 p=root/name; p.write_text(p.read_text()+f'''\n\n## Lotes de torrents e monitoramento\n\nUse `eazy --torrent-list` para criar `~/.config/eazy/torrents.list` a partir dos torrents da fila. Edite o arquivo deixando um magnet ou `.torrent` por linha. Execute `eazy-tor --list ~/.config/eazy/torrents.list --log ~/.config/eazy/torrents.log`. O processamento é sequencial, continua após falhas e exibe resumo; use `--stop-on-error` quando necessário. O log persistente permite acompanhar o lote com `tail -f ~/.config/eazy/torrents.log`.\n''')
p=root/'CHANGELOG.md'; p.write_text(p.read_text().replace('# Changelog\n',f'# Changelog\n\n## {version} — lotes e monitoramento torrent\n- `eazy --torrent-list` cria lista a partir da fila.\n- `eazy-tor --list` processa lotes com resumo, log e opção de parar em erro.\n'))
p=root/'packaging/eazy/debian/control'; p.write_text(p.read_text().replace('3.9.4',version))
p=root/'packaging/eazy/debian/changelog'; p.write_text(f'''eazy ({version}) unstable; urgency=medium\n\n  * Add torrent batch lists, persistent logs and progress summaries.\n  * Add eazy --torrent-list to export queued torrent items.\n\n -- eazy contributors <vapesmadcat-blip@users.noreply.github.com>  Fri, 19 Sep 2026 02:03:00 +0000\n\n'''+p.read_text())

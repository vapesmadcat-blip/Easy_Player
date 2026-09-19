from pathlib import Path
root=Path('/home/ubuntu/easy_player_current')
version='3.7.0'
p=root/'eazy.1'; s=p.read_text().replace('eazy 3.6.1', 'eazy 3.7.0')
block='''\n.SH DOWNLOAD OPTIONS\nLinks diretos usam automaticamente o downloader configurado; não é necessário\nescolher a ferramenta a cada download. O padrão é\n.B aria2c .\nLinks de páginas de vídeo continuam usando\n.BR yt-dlp .\n.P\nEm\n.B F9 → Downloads — downloader/Tor/parâmetros\no usuário pode escolher aria2c, Axel, wget ou yt-dlp, ativar Tor e informar\nparâmetros extras por ferramenta. O Tor usa SOCKS5 em\n.B 127.0.0.1:9050\ne precisa estar ativo no sistema.\n.P\nO Axel usa por padrão\n.B "--insecure -n 4" .\nAs opções ficam em\n.B ~/.config/eazy/config\nnas variáveis\n.B DOWNLOAD_ENGINE , DOWNLOAD_TOR , DOWNLOAD_ARIA_ARGS , DOWNLOAD_AXEL_ARGS ,\n.B DOWNLOAD_WGET_ARGS\ne\n.B DOWNLOAD_YTDLP_ARGS .\n'''
if '.SH DOWNLOAD OPTIONS' not in s: s=s.replace('.SH MAINTENANCE',block+'.SH MAINTENANCE',1)
p.write_text(s)
for name in ['README.md','GUIA_RAPIDO.md','EAZY_EXPLICADO.md']:
 p=root/name; x=p.read_text().replace('3.6.1',version); p.write_text(x)
p=root/'CHANGELOG.md'; p.write_text(p.read_text().replace('# Changelog\n', '# Changelog\n\n## 3.7.0 — downloader automático, Tor e parâmetros\n- Links diretos usam automaticamente o downloader configurado; default: aria2c.\n- Vídeos continuam usando yt-dlp automaticamente.\n- F9 permite trocar downloader, ativar Tor e editar parâmetros.\n'))

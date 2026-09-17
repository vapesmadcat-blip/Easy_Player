from pathlib import Path
p=Path('/home/ubuntu/easy_player_current/eazy.1')
s=p.read_text()
s=s.replace('''\.B Enter
Tocar / abrir só o item sob o cursor; entrar em pasta; abrir playlist
.BR .m3u .
''','''\.B Enter
Tocar / abrir só o item sob o cursor; entrar em pasta; abrir playlist
.BR .m3u .
Em um arquivo
.BR .deb ,
mostra os metadados e oferece instalação confirmada pelo APT.
''',1)
s=s.replace('eazy-gnome_3.3.6_all.deb','eazy-gnome_3.5.0_all.deb').replace('eazy-kde_3.3.6_all.deb','eazy-kde_3.5.0_all.deb')
marker='.SH BUGS\n'
insert='''.SH DISPLAY FORMAT
A lista principal e os resultados de busca exibem as informações no formato
.B TAM · DATA · TIPO .
O tamanho aparece primeiro para facilitar a comparação. As cores das linhas
seguem o ciclo visual de três cores
.BR idx3 ;
essa alternância é apenas visual e não indica codec ou qualidade do vídeo.
.SH DEBIAN PACKAGE INSTALLATION
Ao posicionar o cursor sobre um arquivo
.BR .deb
 e pressionar
.BR Enter ,
o eazy mostra nome, versão e descrição, pede confirmação e executa:
.nf
sudo apt-get install -y ./pacote.deb
.fi
A instalação não ocorre sem confirmação. Se houver dependências pendentes,
use
.BR "sudo apt-get -f install" .
'''
if '.SH DISPLAY FORMAT' not in s:
    s=s.replace(marker, insert+marker, 1)
p.write_text(s)

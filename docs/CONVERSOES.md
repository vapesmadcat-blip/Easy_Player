# Conversões e seleção

No **Ctrl-K → C (Conversões)**, o eazy usa os **arquivos já marcados** (Tab/Espaço).

- 1 arquivo do tipo certo → converte direto (sem reabrir fzf)
- Vários vídeos/imagens → lote (`*_convertido.mp4` / `*_convertida.png`)
- Várias imagens → PDF usa todas as imagens da seleção
- Se a seleção não tiver arquivos do tipo pedido → lista a pasta atual

```bash
./apply-eazy-conv-sel.sh
sudo cp eazy /usr/local/bin/eazy
```

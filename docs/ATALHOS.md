# Atalhos de teclado (eazy 3.2)

## Como usar

1. Abra o eazy e pressione **F9**
2. Escolha **Atalhos de teclado**
3. Selecione a ação e digite o novo atalho no formato **fzf**:
   - `ctrl-a` … `ctrl-z`
   - `f1` … `f12`
   - `alt-d`, `insert`, `del`, `q`

4. **Salvar e voltar** grava em `~/.config/eazy/keys`

## Aplicar o patch no código-fonte

```bash
cd Easy_Player
./apply-eazy-f9-keys.sh
sudo cp eazy /usr/local/bin/eazy
```

## Restaurar padrões

No menu de atalhos: **Restaurar padrões**.

## Arquivo de config

`~/.config/eazy/keys` — pode editar à mão e reiniciar o eazy.

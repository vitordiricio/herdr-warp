# Warp Gruvbox para Herdr

Este repositório fornece uma receita de personalização do Noctua. Leia o README e as opções do instalador antes de instalar.

1. Verifique se o Herdr está instalado e se JetBrainsMono Nerd Font está disponível.
2. Clone este repositório. Execute `python3 scripts/install.py --dry-run` para conferir os arquivos.
3. Execute `python3 scripts/install.py --activate` com o Herdr aberto. Use `--ctrl-v` somente se o usuário também quiser esse atalho.
4. Confira `herdr-app status` e a janela. Não altere o zoom sem solicitação: o layout já define o tamanho-base 13.

O instalador obtém o Noctua diretamente da origem, na revisão fixada, e verifica os hashes antes de gerar os mods. Não requer Noctua previamente instalado. Grava somente o layout/tema Warp Gruvbox, mods `warp-*`, fontes e licenças; Ctrl+V é opcional. Arquivos substituídos são copiados para um backup antes da instalação.

Preserve spaces, abas, splits, Agents, Idle e ações existentes. Não copie estados ou sessões de outro usuário, não sobrescreva `settings.json`, não edite `layouts/.state/` e não modifique os mods originais `noctua-*` ou os componentes internos `frame/`.

Esta receita não publica automaticamente o projeto na galeria do Herdr.

# Warp Gruvbox para Herdr

Este repositório fornece uma receita de personalização do Noctua. Leia o README e as opções do instalador antes de instalar.

1. Verifique se o Herdr está instalado e se JetBrainsMono Nerd Font está disponível.
2. Clone este repositório. Execute `python3 scripts/install.py --dry-run` para conferir os arquivos.
3. Use Python 3.11 ou posterior. Execute `python3 scripts/install.py --activate` com o Herdr aberto. Use `--ctrl-v` somente se o usuário também quiser esse atalho. A instalação também define `notes = false` no core, preservando as outras opções e criando backup quando há substituição.
4. Confira `herdr-app status` e a janela. Não altere o zoom sem solicitação: o layout já define o tamanho-base 13.
5. O botão Detailed view habilita os acordeões de abas/splits; o botão à direita de Machines alterna Agents e Idle. Não copie preferências pessoais de outro computador.

As integrações de nomes de sessão do Codex e Antigravity são opcionais, descritas em integrations/README.md. O instalador principal não modifica esses CLIs. As notificações nativas do Herdr ficam inalteradas.

Antes de redistribuir derivados, leia THIRD_PARTY.md: a licença geral do Noctua não está declarada; baixar a dependência na instalação não resolve essa pendência. Os dois SVGs originais do Warp estão sob AGPLv3, não MIT.

O instalador obtém o Noctua diretamente da origem, na revisão fixada, e verifica os hashes antes de gerar os mods. Não requer Noctua previamente instalado. Grava o layout/tema Warp Gruvbox, mods `warp-*`, fontes e licenças, além de desativar mensagens automáticas em `${XDG_CONFIG_HOME:-~/.config}/herdr-core/config.toml`; Ctrl+V é opcional. Arquivos substituídos são copiados para um backup antes da instalação. O manifesto registra separadamente o destino e o backup da configuração do core. Para destinos isolados, use `--home` e `--core-home` juntos. Dry run não escreve nos destinos. Não reinicie o core nem as sessões para aplicar essa preferência.

Preserve spaces, abas, splits, Agents, Idle e ações existentes. Não copie estados ou sessões de outro usuário, não sobrescreva `settings.json`, não edite `layouts/.state/` e não modifique os mods originais `noctua-*` ou os componentes internos `frame/`.

Esta receita não publica automaticamente o projeto na galeria do Herdr.

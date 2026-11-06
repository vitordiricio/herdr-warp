# Créditos e licenças

## Camada de personalização

Os scripts, a ilustração e a documentação originais de herdr-warp estão sob a [licença MIT](LICENSE), copyright 2026 Vitor Diricio. Essa licença não substitui licenças de terceiros nem concede direitos sobre código obtido de outros projetos.

## Noctua

- Origem: https://github.com/othavi0/noctua-layout
- Revisão: `f42f701e85c3e99b04eca721a240144f8f67c9ef`.
- Autor: othavi0.
- A revisão não contém uma licença geral declarada. Os mods completos não são redistribuídos neste repositório; o instalador obtém os arquivos necessários diretamente da origem e aplica a personalização localmente.
- As chaves de estado `noctua.*` foram mantidas para preservar a compatibilidade dos componentes. A paleta de espaços e sua lógica são do Noctua, inspiradas em Sanzo Wada; a estrutura original também cita T3 Code.

## Herdr

https://github.com/herdrdev/herdr-app — Apache-2.0. O Noctua se baseia nos mods do Herdr. O app, seu core e seus assets de programas não são incluídos. Uma cópia do aviso de licença está em [`licenses/Herdr-Apache-2.0.txt`](licenses/Herdr-Apache-2.0.txt).

## Warp

https://github.com/warpdotdev/warp — revisão de referência `f7fc2f2a08a3aa446baa23960710e630c5defd6e`.

Os SVGs `assets/warp/terminal.svg` e `assets/warp/folder.svg` vêm de `app/assets/bundled/svg/`. São redistribuídos com o aviso [MIT do Warp](licenses/Warp-MIT.txt), copyright 2020–2026 Denver Technologies, Inc.

As medidas e proporções da interface foram estudadas principalmente em:

- `app/src/workspace/view/vertical_tabs.rs`
- `app/src/ui_components/icon_with_status.rs`
- `crates/warp_core/src/ui/theme/color.rs`
- `crates/warpui_core/src/elements/gui/text.rs`

## Roboto

Os arquivos em `fonts/` são as fontes originais distribuídas pelo Warp em `app/assets/bundled/fonts/roboto/`, na revisão acima. Permanecem sob a SIL Open Font License 1.1, com o aviso em [`fonts/LICENSE-Roboto-Warp.txt`](fonts/LICENSE-Roboto-Warp.txt). Não foram modificados.

## Outros recursos

- Os demais ícones dos mods são obtidos com o Noctua e derivam do Lucide e Feather. Os avisos ISC/MIT estão em [`licenses/Lucide.txt`](licenses/Lucide.txt).
- Gruvbox: esquema de cores criado por [morhetz](https://github.com/morhetz/gruvbox), usado aqui conforme a aparência Gruvbox Dark do Warp e a configuração do Ghostty.
- JetBrainsMono Nerd Font é um requisito externo, sem binários distribuídos neste repositório.

Os nomes e marcas identificam suas origens. Este projeto independente não é endossado pelo Herdr, Warp, Noctua ou pelos autores das fontes e ícones.

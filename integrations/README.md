# Nomes de sessão dos CLIs

O Herdr recebe o nome publicado pelo CLI como título do terminal. Renomear uma conversa internamente só aparece no layout quando o CLI também publica essa alteração. Estas integrações são opcionais e não modificam o código dos CLIs ou do Herdr.

## Antigravity (`agy`)

O helper lê o JSON que o AGY envia ao comando `title`, imprime somente `conversation_title` e usa `Antigravity` quando não há nome. Não grava o payload, não lê históricos e não envia dados pela rede.

```sh
# A partir da raiz deste repositório:
python3 integrations/antigravity/install.py --dry-run
python3 integrations/antigravity/install.py
```

O instalador copia `title.py` para `~/.gemini/antigravity-cli/` e mescla somente a chave `title` de `settings.json`, preservando as demais configurações. Faz backup dos arquivos anteriores em `backups/herdr-warp-title-<data>/`, preservando as permissões do arquivo de configuração. Use `--home /outro/destino` se necessário.

Na sessão AGY já aberta, digite diretamente:

```text
/title on
```

O exemplo de configuração está em [antigravity/settings.example.json](antigravity/settings.example.json). Não substitua seu arquivo inteiro pelo exemplo.

Ao operar pelo Herdr, digite o slash command diretamente na interface. `hc send` a partir de outro agente pode envolver o texto em uma marcação de mensagem entre agentes, fazendo com que o CLI o interprete como um prompt. O instalador não envia comandos a sessões abertas.

Validado com AGY 1.5.2 no Linux. Referências oficiais: [comando de título](https://antigravity.google/docs/cli/title/), [campo conversation_title](https://antigravity.google/docs/cli/statusline#available-json-fields) e [ativação com /title on](https://antigravity.google/docs/cli/commands/title).

Para desfazer, restaure `settings.json` do backup correspondente e, se existia, o `title.py` anterior. Se não havia configuração, remova somente a chave `title` adicionada. Na sessão aberta, `/title off` desativa a atualização.

## Codex

Execute `/title` no Codex e escolha os campos desejados: mantenha o nome da conversa/thread e retire projeto/diretório se não quiser um sufixo de pasta. A escolha é salva pelo próprio Codex em `tui.terminal_title`.

Nenhum arquivo de configuração pessoal do Codex é distribuído ou modificado por este projeto. Consulte a [documentação oficial de /title](https://learn.chatgpt.com/docs/cli/slash-commands#configure-terminal-title-items-with-title).

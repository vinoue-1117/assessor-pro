---
name: live-run
description: 'Roda o avaliador de transcript sobre o export de uma conversa do bot real (live run), sem ator, e ajusta o conversor do export quando o formato muda. Trigger: export de transcript do Grok Bot trazido pelo dono, "rodar o live run", "avaliar o transcript do bot real".'
---

# Live run

O dono traz a pasta do export de uma conversa do bot real. O `scripts/live-run.py` converte o trecho do fluxo para o `transcript.md` que o agente `avaliador-transcript` lê, roda o avaliador e grava o relatório fora do repositório. Esta skill escolhe o trecho e, quando o export muda de formato, ajusta o conversor contra o contrato abaixo.

O export tem dado de cliente. Nada dele entra no repositório: nem trecho em teste, nem exemplo nesta skill, nem texto de issue ou PR.

## Passos

1. Rode `python scripts/live-run.py <pasta do fluxo> <pasta do export>`, com a pasta do fluxo em `evals/<bot>/fluxo/<fluxo>`. Sem `--desde`, o script lista as mensagens do dono (marca, arquivo e linha, começo do texto) e para.
2. Escolha o trecho. `--desde` é a mensagem do dono que pede o fluxo. `--ate` é a primeira mensagem do dono, depois dela, que pede outra coisa (o export do transcript, por exemplo); sem `--ate`, o trecho vai até o fim. Mensagem do dono que continua o fluxo ("pode publicar") fica dentro. Se a lista não deixar claro onde o fluxo começa ou acaba, pergunte ao dono.
3. Rode de novo com `--desde` e, se for o caso, `--ate`. `--saida` é opcional e tem que ser uma pasta nova, fora do repositório.
4. Se o script parar com `formato desconhecido`, siga a seção abaixo e volte ao passo 3.
5. Responda ao dono com o caminho do `relatorio.md` e o resumo do topo do relatório.

## Formato desconhecido

O script para, com o arquivo e a linha do export, quando o export tem algo fora do contrato de entrada. Não edite o export.

1. Leia a linha apontada no export e diga ao dono o que mudou.
2. Ajuste o `scripts/live-run.py` para que a entrada nova saia no contrato de saída. Formato que o script não reconhece continua parando o script: não troque a parada por um rótulo genérico.
3. Acrescente o caso ao teste do conversor em `tests/test_live_run.py`, com ids e textos inventados.
4. Rode `python scripts/check.py`.
5. Mudança no contrato (um papel ou um bloco novo, uma marca nova de mensagem) entra nesta skill no mesmo diff.

## Contrato de entrada

A pasta do export, gravada pelo bot com a ferramenta `ReadTranscript` da plataforma:

- Um `.jsonl` da sessão principal: o único sem `sand-subagent-` no nome.
- Um `.jsonl` por subagente, com `sand-subagent-<id>` no nome.
- Cada linha é `{"role": ..., "message": {"content": [blocos]}}`.

| Papel | Blocos |
| --- | --- |
| `user` | `text` |
| `assistant` | `text`, `thinking`, `tool_use` (`id`, `name`, `input`) |
| `tool` | `tool_result` (`tool_use_id`, `name`, `result`) |

- **Input.** O `input` do `tool_use` é um objeto ou um JSON em texto.
- **Mensagens de usuário na sessão principal.** A do dono tem `[tNu]` logo depois de `<user_query>`. A da plataforma tem `[GROK_BOT_HIDDEN_PROMPT]` ou `<memory_context>`.
- **Subagente.** A chamada é um `CallDynamicTool` com `toolName` `Task`. O `arguments` traz `subagent_type`, e traz `resume` quando o subagente é retomado. O resultado traz `sand-subagent-<id>`.
- **Subagente retomado.** Ele continua no mesmo arquivo. Cada mensagem `user` do arquivo do subagente é a entrada de uma chamada, na ordem.
- **Eventos repetidos.** O export repete chamada e resultado com o mesmo id depois de um `<memory_context>`.
- **Teto.** Todo bloco com mais de uns 4.000 caracteres vem com o meio trocado por `...`. Não há opção da `ReadTranscript` que traga o bloco inteiro.

## Contrato de saída

Na pasta de execução, o `transcript.md`, o `page.md` (se o trecho tem `WriteCanvas`) e o `relatorio.md`. O `transcript.md` é o que o avaliador lê:

- O topo diz de que arquivo e de que trecho ele veio, por onde o bot entrega a resposta ao dono (`SendToUser`) e onde está a Page.
- `## passo <N>: <quem> chama <ferramenta> (<nome>) [<arquivo>:<linha>]`, um por chamada, numerado em sequência. `<quem>` é `bot` ou `subagente <tipo> do passo <N da chamada>`. O `<nome>` da chamada de subagente é `Task <tipo>`, com `, retomada` quando retoma.
- `### resultado do passo <N> (<nome>), para <quem> [<arquivo>:<linha>]`. Nenhum resultado fica sem o passo da chamada.
- `### mensagem do dono [tNu]`, `### mensagem da plataforma`, `### entrada para <quem>`, `### texto de <quem>` e `### raciocinio de <quem>`, cada um com `[<arquivo>:<linha>]`.
- O trecho do subagente entra logo depois do resultado da chamada que o iniciou ou retomou.
- Chamada repetida entra uma vez.
- O `page.md` é o `contents` do último `WriteCanvas` do trecho. Edição posterior da Page (`EditCanvas`) só aparece nos passos.

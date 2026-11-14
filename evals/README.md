# Evals

Material de avaliação dos bots. Fica fora de `bots/`, que guarda só o que o bot instala e usa.

Uma mudança de skill é avaliada por três eixos independentes:

| Eixo | Pergunta |
| --- | --- |
| Fluxo | o bot segue a skill? |
| Acerto | a resposta está certa, contra uma referência conhecida? |
| Gosto | qual formato de saída é melhor de ler? O dono é o juiz |

```text
evals/<bot>/
  fluxo/<fluxo>/   cenario.md, erros.md e, se o fluxo usar subagente, agentes.json
```

O eixo de acerto do Analista está em [`bots/analista/evals/revisor/`](../bots/analista/evals/revisor), pelo `claude plugin eval`.

## Fluxo: dry run

Um ator faz o papel do bot sobre um cenário, e um avaliador lê o transcript. A rodada vai do disparo ao relatório sem o dono no meio e para no relatório.

`python scripts/dry-run.py evals/analista/fluxo/tese`

| Peça | O que é |
| --- | --- |
| `cenario.md` | `## Pedido`: a mensagem do dono. `## Plataforma`: o que substitui, no computador de teste, cada parte da plataforma do bot (pastas, download da `stable`, subagente, Page). `## Para o avaliador`: o que não conta como desvio e o que a rodada não mede |
| `erros.md` | as falhas já vistas no fluxo, cada uma com o que se vê no transcript e a instrução da skill que ela contraria. Falha nova que o relatório aponta entra aqui |
| `agentes.json` | os subagentes que a plataforma tem e o Claude Code não, no formato do `--agents` |
| [`scripts/dry-run.py`](../scripts/dry-run.py) | monta a pasta de execução, roda o ator e o avaliador e grava tudo nela |
| [`.claude/agents/avaliador-transcript.md`](../.claude/agents/avaliador-transcript.md) | o papel do avaliador. Cada desvio cita o passo do transcript e a instrução da skill que ele contraria |

### O ator

`claude -p`, headless, com Sonnet, pelo login do plano. O script tira a `ANTHROPIC_API_KEY` do ambiente do ator e do avaliador: com ela definida, o `claude -p` se autentica pela chave e cobra pela API. Ele roda numa pasta de execução fora do repositório, com as skills da branch copiadas para `.claude/skills/`. O prompt de sistema é o do Claude Code com o `## Perfil` do `bot.md` e a seção `## Plataforma` do cenário. As skills são as da branch, não as da `stable`: o cenário troca o endereço do download pelo `file:///` do repositório.

As instruções de quem roda ficam fora do contexto do ator: `--setting-sources project` tira as skills e as rules do usuário, e o `claudeMdExcludes` tira o `~/.claude/CLAUDE.md`. As skills que vêm com o Claude Code continuam visíveis para ele. Ferramentas: Bash (o do Git for Windows), leitura e escrita de arquivo, `WebSearch`, `WebFetch`, `Agent` e `Skill`; o que pediria permissão fora dessa lista é negado e aparece no transcript. O subagente roda em primeiro plano, como o `Task` da plataforma.

O ator usa o `{python}` do cenário, que é o Python que roda o `dry-run.py`. Esse Python precisa ter o `yfinance`: o `python3` do Git Bash no Windows não tem.

### O avaliador

Se o ator sai com código diferente de zero, a rodada fica incompleta: o script grava o transcript e para sem chamar o avaliador, porque um relatório sobre um fluxo cortado mediria a queda e não a skill.

O agente `avaliador-transcript`, com Opus, roda a partir da raiz do repositório e lê só arquivos. Ele escreve o relatório de desvios: cada desvio com o passo do transcript e a instrução da skill, as entradas do `erros.md` que não apareceram, as lacunas da skill e o que a rodada não mediu. Não há nota nem régua automática.

### A pasta de execução

Uma pasta temporária nova por rodada, ou a de `--saida`. O script recusa pasta dentro do repositório.

| Arquivo | Conteúdo |
| --- | --- |
| `transcript.jsonl` | o stream do ator (`--output-format stream-json`), com o texto dos subagentes |
| `transcript.md` | a versão legível: um passo por chamada de ferramenta, bloco longo cortado com a linha do jsonl |
| `page.md` | a Page, se o ator publicou |
| `relatorio.md` | o relatório do avaliador |
| `sistema.md` | o que foi acrescentado ao prompt de sistema do ator (`--append-system-prompt-file`) |
| `ator.err` | o stderr do ator |
| `workspace/`, `tmp/` | o que o ator gravou no lugar de `/workspace/` e `/tmp/` |

O repositório é público: transcript e relatório não entram nele.

### Limites

- O ator é Claude, não o modelo do bot. O dry run compara versões de uma skill. O comportamento absoluto é o do bot real.
- O fluxo usa dado público de verdade (Banco Central, Tesouro Transparente, busca na web). A mesma rodada não se repete igual de um dia para o outro.
- A plataforma não roda: o download da `stable`, a Page e o subagente da plataforma são substituídos pelo que o cenário descreve.

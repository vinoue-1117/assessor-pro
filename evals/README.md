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
  acerto/<caso>/      rodar.py, a entrada, o gabarito, os critérios do juiz (graders/) e o README do caso
  fluxo/<fluxo>/      cenario.md, anti-patterns.md e, se o fluxo usar subagente, agentes.json
  gosto/<pergunta>/   cenario.md, variantes/<nome>/ e, depois que o dono decide, decisao.md
```

O eixo de acerto roda pelo `claude plugin eval`. O caso do Analista está em [`analista/acerto/revisor/`](analista/acerto/revisor), com o README dele.

## Fluxo: dry run

Um ator faz o papel do bot sobre um cenário, e um avaliador lê o transcript. A rodada vai do disparo ao relatório sem o dono no meio e para no relatório.

`python scripts/dry-run.py evals/analista/fluxo/tese`

| Peça | O que é |
| --- | --- |
| `cenario.md` | `## Pedido`: a mensagem do dono. `## Plataforma`: o que substitui, no computador de teste, cada parte da plataforma do bot (pastas, download da `stable`, subagente, Page). `## Para o avaliador`: o que não conta como desvio e o que a rodada não mede |
| `anti-patterns.md` | as falhas já vistas no fluxo, cada uma com o que se vê no transcript e a instrução da skill que ela contraria. A seção `## O que entra` diz quando a falha nova que o relatório aponta entra |
| `agentes.json` | os subagentes que a plataforma tem e o Claude Code não, no formato do `--agents` |
| [`scripts/dry-run.py`](../scripts/dry-run.py) | monta a pasta de execução, roda o ator e o avaliador e grava tudo nela |
| [`.claude/agents/avaliador-transcript.md`](../.claude/agents/avaliador-transcript.md) | o papel do avaliador. Cada desvio cita o passo do transcript e a instrução da skill que ele contraria |

### O ator

`claude -p`, headless, pelo login do plano, com o modelo de `--modelo` (padrão: `sonnet`; vale também no gosto). O `--modelo` muda só o ator: o subagente do `agentes.json` fica com o modelo escrito nele. O script tira a `ANTHROPIC_API_KEY` do ambiente do ator e do avaliador: com ela definida, o `claude -p` se autentica pela chave e cobra pela API. Ele roda numa pasta de execução fora do repositório, com as skills da branch copiadas para `.claude/skills/`. O prompt de sistema é o do Claude Code com o `## Perfil` do `bot.md` e a seção `## Plataforma` do cenário. As skills são as da branch, não as da `stable`: o cenário troca o endereço do download pelo `file:///` do repositório.

As instruções de quem roda ficam fora do contexto do ator: `--setting-sources project` tira as skills e as rules do usuário, e o `claudeMdExcludes` tira o `~/.claude/CLAUDE.md`.

O ator enxerga só as skills do bot. As skills que vêm com o Claude Code saem pelo `--settings`: o `disableBundledSkills` tira quase todas, e o `skillOverrides` com `"off"` tira por nome as que sobram no `init` (`ESCONDIDAS` no script). O `--allowedTools` com `Skill(<skill do bot>)` não serve para isso: ele só pré-aprova, e o `dontAsk` não nega skill que não pede aprovação. A pesquisa e os testes estão em [`docs/research/skills-embutidas-no-claude-p.md`](../docs/research/skills-embutidas-no-claude-p.md). Uma skill nova do Claude Code, que escape das duas opções, aparece na seção `## fora do bot` no topo do `transcript.md`: as skills de fora do bot listadas no `init` e cada chamada de `Skill` com nome que não é de pasta do bot, que também fica marcada no passo. A chamada cujo resultado veio com erro leva `recusada`: o ator tentou, e a skill não carregou. O avaliador cita essa seção no relatório, separando skill só vista, chamada recusada e carga, e o `index.html` do gosto a mostra na célula da amostra.

Ferramentas: Bash (o do Git for Windows), leitura e escrita de arquivo, `WebSearch`, `WebFetch`, `Agent` e `Skill`; o que pediria permissão fora dessa lista é negado e aparece no transcript. O subagente roda em primeiro plano, como o `Task` da plataforma.

O ator usa o `{python}` do cenário, que é o Python que roda o `dry-run.py`. Esse Python precisa ter o `yfinance`: o `python3` do Git Bash no Windows não tem.

### O avaliador

Se o ator sai com código diferente de zero, a rodada fica incompleta: o script grava o transcript e para sem chamar o avaliador, porque um relatório sobre um fluxo cortado mediria a queda e não a skill.

O agente `avaliador-transcript`, com Opus, roda a partir da raiz do repositório e lê só arquivos. Ele escreve o relatório de desvios: cada desvio com o passo do transcript e a instrução da skill, as entradas do `anti-patterns.md` que não apareceram, as lacunas da skill e o que a rodada não mediu. Não há nota nem régua automática.

### A pasta de execução

Uma pasta temporária nova por execução, ou a de `--saida`. O script recusa pasta dentro do repositório. Com `--rodadas N`, a execução roda o ator e o avaliador N vezes, cada rodada na sua pasta, `rodada-<n>`, dentro da pasta da execução; com uma rodada só, que é o padrão, a pasta da execução é a da rodada. Rodada em que o ator cai ou o avaliador falha não interrompe as seguintes: o script segue, imprime a tabela de métricas e, no fim, sai com erro listando as rodadas incompletas.

Para guardar as rodadas, crie o `.env` na raiz do repositório a partir do [`.env.example`](../.env.example), com a pasta de dados privada em `ASSESSOR_EVALS_DADOS`. No fim de cada rodada, completa ou incompleta, o script copia a pasta de execução inteira para `<pasta de dados>/execucoes/<bot>/<data>-<fluxo>-dry-run`; a segunda rodada do dia ganha o sufixo `-2`. O ator roda sempre na pasta de execução, nunca na pasta de dados, que só armazena. Sem o `.env`, nada é copiado. O `.env` não é versionado.

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

### Métricas

No fim da execução, o script imprime as tabelas de métricas das rodadas dela. As mesmas tabelas saem, sem rodar nada, para rodadas já guardadas:

`python scripts/dry-run.py --metricas <pasta> [<pasta> ...]`

Cada `transcript.jsonl` dentro das pastas, em qualquer nível, é uma rodada. A tabela agrupa só pelo modelo do ator, então as pastas têm que ser execuções do mesmo fluxo: uma pasta de `execucoes/<bot>` inteira junta fluxos diferentes e amostras de gosto na mesma linha. Pasta que não existe para o script. Cada métrica traz a mediana das rodadas e, se elas diferem, a faixa entre parênteses. A rodada cujo stream não tem um `result` de sucesso (sem o evento, ou com `subtype` diferente de `success` ou `is_error`: ator que caiu no meio) fica fora, com aviso.

- A primeira tabela tem uma linha por modelo do ator (o `model` do evento `init`), com o número de rodadas, os turnos e os minutos.
- A segunda tem uma linha por modelo do ator e modelo usado na rodada (o ator, o subagente e o que as ferramentas chamam por dentro), com as requisições e os tokens só daquele modelo. Os tokens de um modelo nunca entram na linha de outro. A rodada que não usou o modelo entra com zero na mediana.

| Métrica | De onde vem |
| --- | --- |
| `requisicoes no stream` | as mensagens distintas (`message.id`) do ator e dos subagentes, pelo `model` de cada mensagem. Uma resposta com vários blocos chega em vários eventos com o mesmo id e conta uma vez. A ferramenta que chama um modelo por dentro (o `WebFetch` resume a página com o Haiku) não emite mensagem: esse modelo aparece com tokens e zero requisições |
| `turnos` | o `num_turns` do `result`, que conta cada resultado de ferramenta do ator; por isso passa das requisições quando o ator chama ferramentas em paralelo |
| `entrada`, `cache lido`, `cache gravado`, `saida` | os tokens do modelo no `modelUsage` do `result`, que separa por modelo e inclui os subagentes e as chamadas internas das ferramentas. O `usage` de cada evento do stream não serve, porque o de saída é parcial |
| `minutos` | o `duration_ms` do `result` |

A métrica principal é requisições e tokens. O tempo varia com a carga da máquina e só se compara pela mediana de várias rodadas.

Para comparar modelos, rode o mesmo fluxo com cada um e passe as pastas das execuções ao `--metricas`:

`python scripts/dry-run.py evals/analista/fluxo/tese --modelo haiku --rodadas 3`

### Limites

- O ator é Claude, não o modelo do bot. O dry run compara versões de uma skill. O comportamento absoluto é o do bot real.
- O fluxo usa dado público de verdade (Banco Central, Tesouro Transparente, busca na web). A mesma rodada não se repete igual de um dia para o outro.
- A plataforma não roda: o download da `stable`, a Page e o subagente da plataforma são substituídos pelo que o cenário descreve.

## Gosto: variantes lidas pelo dono

N variantes de uma instrução do bot geram amostras sobre a mesma entrada, e o dono lê e escolhe. A pergunta muda a cada rodada (layout, persona, template de blocos, playbook), então cada rodada começa numa sessão que decide com o dono:

- a pergunta e as variantes;
- o ponto de partida: o fluxo inteiro, ou só a escrita sobre arquivos congelados de uma rodada anterior;
- o número de amostras de cada variante;
- onde o dono lê (o navegador do computador, no caso de uma Page em HTML).

O que não muda entre rodadas:

- Todas as variantes recebem a mesma entrada: o mesmo `## Pedido`, a mesma `## Plataforma` e, se houver, a mesma pasta de partida. A diferença entre as amostras é só a sobreposição.
- As amostras, os transcripts e os arquivos congelados ficam fora do repositório, na pasta de dados.
- A decisão do dono entra em `gosto/<pergunta>/decisao.md`: a pergunta, as variantes, o que ele viu e o que entra na skill.

`python scripts/dry-run.py evals/analista/gosto/layout --variantes --amostras 2 --partida <pasta>`

| Peça | O que é |
| --- | --- |
| `variantes/<nome>/` | só os arquivos que mudam em `bots/<bot>/`: `bot.md` (o `## Perfil` dele vai para o prompt de sistema no lugar do perfil do bot) ou arquivos de `skills/<skill>/`, que substituem os da cópia das skills. A variante vazia, com só um `.gitkeep`, é o bot de hoje. Arquivo que o bot não tem, com o mesmo caminho e as mesmas maiúsculas, para o script antes de rodar |
| `--variantes [NOME ...]` | as variantes da rodada; sem nome, todas as pastas de `variantes/`. Sem avaliador |
| `--amostras M` | amostras de cada variante, rodadas uma de cada variante por volta. O `--rodadas` não vale no gosto |
| `--partida PASTA` | os arquivos congelados, só nas pastas `tmp/` e `workspace/`, copiados sobre as da pasta de execução antes de o ator rodar. Qualquer outra coisa na pasta (o `.claude/` de uma rodada anterior, por exemplo) para o script antes de rodar. Cenário com a seção `## Partida` exige essa opção; a seção diz o que a pasta tem que ter |

Cada amostra roda na sua pasta de execução, `<variante>-<n>`, dentro da pasta da rodada, com os mesmos arquivos do dry run de fluxo. A pasta da rodada tem um `index.html`, uma linha por variante e uma coluna por amostra, com o link da `page.html`, o tempo e o transcript de cada uma. Com o `.env`, a rodada inteira é copiada para `<pasta de dados>/execucoes/<bot>/<data>-<pergunta>-gosto`; sem ele, fica na pasta temporária.

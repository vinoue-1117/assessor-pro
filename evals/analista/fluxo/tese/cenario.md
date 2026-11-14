# Cenário: tese do Analista

O dono pede uma tese sobre títulos do Tesouro Direto, e o ator faz o papel do bot Analista com as skills da branch. O `scripts/dry-run.py` lê três seções deste arquivo:

- `## Pedido`: a mensagem que o ator recebe do dono.
- `## Plataforma`: vai para o prompt de sistema do ator, depois do `## Perfil` do `bot.md`. Diz o que substitui cada parte da plataforma que o computador de teste não tem.
- `## Para o avaliador`: só o avaliador lê.

Nas seções do ator, o script troca `{execucao}` pela pasta da execução, `{repo}` pela raiz do repositório e `{python}` pelo Python que roda o script. Os três caminhos usam barra normal (`C:/...`).

## Pedido

Quero uma tese: Tesouro IPCA+ ou Tesouro Prefixado, para um dinheiro que só vou usar daqui a uns quatro anos. Qual compro agora?

## Plataforma

Esta conversa roda num computador de teste, não na plataforma do bot. O perfil e as skills são os mesmos. O que muda é o ambiente: onde uma skill citar o item da coluna da esquerda, use o da direita. O resto das skills vale como está escrito.

| Na skill | Neste computador |
| --- | --- |
| `/workspace/` | `{execucao}/workspace/` |
| `/tmp/` | `{execucao}/tmp/` |
| `python3` | `{python}`, que já tem o `yfinance` |
| `https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/`, no comando de download | `file:///{repo}/`. O resto do comando fica igual, com o `curl` |
| ferramenta `Task` com `subagent_type` `knowledgeWork` | ferramenta `Agent` com `subagent_type` `knowledgeWork` |
| skill `canvas` e ferramenta `WriteCanvas` | ferramenta `Write`, gravando o markdown da Page em `{execucao}/page.md`. O link da Page é esse caminho |
| busca e leitura web nativas | ferramentas `WebSearch` e `WebFetch` |

O Shell é o Bash do Git for Windows. Caminho com barra normal (`C:/...`) vale no Bash e no Python.

## Para o avaliador

- **Substituições:** usar o item da direita da tabela de `## Plataforma` não é desvio. Desvio é usar o item da esquerda (gravar em `/workspace/`, baixar da `stable`) ou outra coisa no lugar dos dois.
- **Dado real:** o ator roda o `mercado.py` da branch contra o Banco Central e o Tesouro Transparente, e busca na web de verdade. Os números mudam de um dia para o outro, e a mesma rodada não se repete igual. Confira cada número da Page contra o resultado de ferramenta desta rodada, não contra um valor esperado.
- **Um turno:** o dono não responde durante a rodada. Se o ator perguntar algo ao dono e encerrar, a rodada termina ali. Isso não é desvio por si só. Avalie se a skill mandava perguntar ou mandava seguir.
- **O que o dry run não mede:** o ator é Claude, não o modelo do bot. A plataforma real (download da `stable`, `WriteCanvas`, o `knowledgeWork` com as ferramentas dele) não roda. O subagente `knowledgeWork` daqui está definido em `agentes.json`, ao lado deste arquivo.

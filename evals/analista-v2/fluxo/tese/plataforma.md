# Plataforma: tese do Analista v2

O ator faz o papel do bot Analista v2 com as skills da branch. Cada cenário de `cenarios/` traz o `## Pedido`, a mensagem que o ator recebe do dono, e pode trazer um `## Para o avaliador` só dele. Este arquivo vale para todos os cenários do fluxo, e o `scripts/dry-run.py` lê três seções dele:

- `## Plataforma`: vai para o prompt de sistema do ator, depois do `## Perfil` do `bot.md`. Diz o que substitui cada parte da plataforma que o computador de teste não tem.
- `## Trocas nas skills`: o ator não lê. O script grava cada troca da tabela nos `.md` da cópia das skills que o ator recebe, e o ator roda os comandos como estão escritos.
- `## Para o avaliador`: só o avaliador lê.

Na seção do ator, na tabela de trocas e no pedido, o script troca `{execucao}` pela pasta da execução e `{python}` pelo Python que roda o script, os dois com barra normal (`C:/...`), e `{repo_url}` pelo endereço `file:///` da raiz do repositório.

## Plataforma

Esta conversa roda num computador de teste, não na plataforma do bot. O perfil e as skills são os mesmos. Os caminhos, o Python e o endereço do download já vêm trocados nas skills: rode os comandos como estão escritos. O que muda além disso: onde uma skill citar o item da coluna da esquerda, use o da direita. O resto das skills vale como está escrito.

| Na skill | Neste computador |
| --- | --- |
| ferramenta `Task` com `subagent_type` `knowledgeWork` | ferramenta `Agent` com `subagent_type` `knowledgeWork` |
| skill `canvas` e ferramenta `WriteCanvas` | ferramenta `Write`, gravando o markdown da Page em `{execucao}/page.md`. O link da Page é esse caminho |
| busca e leitura web nativas | ferramentas `WebSearch` e `WebFetch` |
| leitura web nativa de PDF | baixar o PDF com `curl` para `{execucao}/tmp/` e extrair o texto com `pypdf`, no `{python}`, que já tem o `pypdf` |

O Shell é o Bash do Git for Windows. Caminho com barra normal (`C:/...`) vale no Bash e no Python.

## Trocas nas skills

| Na skill | Na cópia |
| --- | --- |
| `/workspace/` | `{execucao}/workspace/` |
| `/tmp/` | `{execucao}/tmp/` |
| `python3` | `{python}` |
| `https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/` | `{repo_url}/` |

## Para o avaliador

- **Substituições:** usar o item da direita da tabela de `## Plataforma` não é desvio. Desvio é usar o item da esquerda ou outra coisa no lugar dos dois.
- **Trocas nas skills:** as skills que o avaliador lê são a cópia que o ator recebeu, com as trocas de `## Trocas nas skills` já gravadas. O comando que o ator roda tem que ser igual ao da cópia. Gravar em `/workspace/` ou baixar da `stable` é desvio.
- **Dado real:** o ator roda o `mercado.py` da branch contra o `yfinance`, o Banco Central e o Tesouro Transparente, e busca na web de verdade. Os números mudam de um dia para o outro, e a mesma rodada não se repete igual. Confira cada número da Page contra o resultado de ferramenta desta rodada, não contra um valor esperado.
- **Um turno:** o dono não responde durante a rodada. Se o ator perguntar algo ao dono e encerrar, a rodada termina ali. Isso não é desvio por si só. Avalie se a skill mandava perguntar ou mandava seguir.
- **O que o dry run não mede:** o ator é Claude, não o modelo do bot. A plataforma real (download da `stable`, `WriteCanvas`, o `knowledgeWork` com as ferramentas dele, a leitura nativa de PDF) não roda. O subagente `knowledgeWork` daqui está definido em `agentes.json`, ao lado deste arquivo. Com um turno só, a resposta do dono à pergunta de modo também não roda: o cenário `sem-modo` termina na pergunta, e o que a `analista-v2-tese` manda fazer com a resposta fica sem rodada.

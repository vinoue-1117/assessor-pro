# Cenário: layout da Page da tese

Pergunta: "faça uma Page visual, com gráficos" funciona como instrução na `analista-tese`, ou a skill precisa descrever a estrutura da Page?

Só a escrita da Page varia. Os dados e o rascunho revisado de uma tese de ação ficam congelados, e toda amostra parte deles. O ator grava a Page como um HTML autocontido, à maneira dele: o dry run não reproduz a Page do Grok Bot, e supor que a preferência se transfere para a plataforma é aposta, não medida.

| Variante | O que muda na seção 5 (Page) da `analista-tese` |
| --- | --- |
| `atual` | nada: texto corrido de buy-side, seção de riscos e seção de fontes |
| `visual-generica` | uma frase pedindo uma Page visual, com gráficos e painéis |
| `visual-estruturada` | a estrutura descrita: painel de indicadores no topo, um gráfico por bloco de argumento, tabela de sinais em semáforo, decisão no fim |

```text
python scripts/dry-run.py evals/analista/gosto/layout --variantes --amostras 2 --partida <pasta de partida>
```

O `scripts/dry-run.py` lê `## Pedido` e `## Plataforma` como no dry run de fluxo, com as mesmas trocas de `{execucao}`, `{python}` e `{repo_url}`. A seção `## Partida` só diz o que a pasta de `--partida` tem que ter: com ela no cenário, o script recusa rodar sem `--partida`.

## Partida

Uma pasta só com `tmp/` (e, se precisar, `workspace/`), copiada sobre a pasta de execução antes de o ator rodar. O script recusa a partida que tiver outra coisa além dessas duas pastas. O `tmp/` traz:

- `tmp/analista-dados-<slug>.json`: o pacote de dados do passo 1 da `analista-tese`;
- `tmp/analista-rascunho-<slug>.md`: o rascunho como o ator o deixou no `tmp/`, que é o que foi à última revisão.

Os dois saem do `tmp/` de uma rodada inteira do fluxo da tese sobre uma ação (histórico, pares e opções dão o que desenhar). Ficam na pasta de dados, fora do repositório.

## Pedido

Escreva a Page da tese. Os dados e o rascunho revisado já estão em `/tmp/`.

## Plataforma

Esta conversa roda num computador de teste, não na plataforma do bot. O perfil e as skills são os mesmos. O que muda é o ambiente: onde uma skill citar o item da coluna da esquerda, use o da direita. O resto das skills vale como está escrito.

| Na skill | Neste computador |
| --- | --- |
| `/workspace/` | `{execucao}/workspace/` |
| `/tmp/` | `{execucao}/tmp/` |
| `python3` | `{python}` |
| skill `canvas` e ferramenta `WriteCanvas` | ferramenta `Write`, gravando a Page como um único arquivo HTML autocontido em `{execucao}/page.html`. Onde a skill diz que o conteúdo da Page é markdown, ele é esse HTML. O link da Page é esse caminho |

Os passos 1 a 4 da `analista-tese` (dados, rascunho e as duas revisões) já rodaram numa conversa anterior deste bot. O pacote `{execucao}/tmp/analista-dados-<slug>.json` e o rascunho `{execucao}/tmp/analista-rascunho-<slug>.md` são o resultado deles e valem como as chamadas de `mercado.py` e as páginas abertas nesta conversa. Não colete dado novo e não rode a revisão de novo: faça os passos 5 e 6 a partir desses dois arquivos, sem mudar número nem conclusão.

O Shell é o Bash do Git for Windows. Caminho com barra normal (`C:/...`) vale no Bash e no Python.

# analista-v2

Bot **Analista v2**: analista de mercado buy-side em pt-BR. Consulta preços com `yfinance` e taxas no Banco Central e no Tesouro Transparente, faz as contas em Python e entrega teses e comparações em Page. Ele escreve a tese com os contras, passa o texto uma vez por um fact_checker, corrige o que foi apontado e publica.

Ficha do bot: [`bot.md`](bot.md).

## Instalar

Cole no chat deste bot para instalar, atualizar um bot já instalado ou conferir se ele está funcionando. Bot de time só se instala por este prompt. Bot pessoal também pode ser instalado pelo [bot construtor](../../docs/grokbot.md#bot-construtor), sem ele. A conferência é pela função, não pelo nome nem pelo título do `bot.md`.

```
Atualize suas skills pelo repositório de bots, caminho analista-v2, seguindo https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/bots/instalar.md.
Antes de começar, confira que você é o bot analista de mercado buy-side em pt-BR (seu nome pode ser outro). Se você for outro bot qualquer, pare e diga que este prompt é para outro bot.
Não apague nem altere nada em `/workspace/analista-v2/`.
No fim, mostre a checklist do instalar.md marcada.
```

## Skills

| Skill | Quando |
| --- | --- |
| `analista-v2-core` | sempre: persona, regras e entrega |
| `analista-v2-mercado` | cotação, histórico, opções via `yfinance`, Selic, CDI e IPCA do Banco Central, taxa do Tesouro Direto, ou conta em Python |
| `analista-v2-tese` | tese, comparação, relatório ou Page, com uma conferência de fatos antes de publicar |

O bot instalado guarda o ponteiro. A skill completa é baixada da branch `stable` a cada uso. Os ponteiros em `ponteiros/` são gerados por `python scripts/gerar-ponteiros.py`. Não edite essa pasta à mão.

Workspace deste bot: `/workspace/analista-v2/` (o script de trabalho fica em `/workspace/analista-v2/mercado.py`). O arquivo da tese e o pacote de dados ficam em `/tmp/analista-v2-*`.

## Tese

| Passo | O que acontece |
| --- | --- |
| Modo | o pedido que diz o modo segue nele ("tese rápida" é o simples; "relatório completo" ou "análise detalhada", o detalhado). O que não diz leva só a linha "Análise simples ou detalhada?", antes de qualquer dado. Se a resposta do dono não escolher, sai o simples |
| Dados | `mercado.py`, páginas abertas (o fundamento, na fonte primária) e contas em Python, gravados no pacote de dados. Sem o dado principal (a cotação ou a taxa do ativo da tese), o bot para aqui e diz qual dado não veio |
| Tese | o bot escreve a tese em markdown, com os riscos e o que faria mudar de ideia. No modo simples, ela já vem nas seções da Page, com os contras |
| Conferência de fatos | uma chamada ao fact_checker, um subagente que recebe a tese, o pacote de dados e as mensagens do dono. Ele devolve uma linha por erro, ou `Sem erros.`, sem veredito |
| Tese final | o bot corrige cada erro, roda de novo a conta que mudou e revê a decisão com os números novos |
| Page | publicada sempre que o dado principal veio. Se a chamada do fact_checker falhar, a tese sai como está e o chat diz que a conferência não rodou |

Os dois modos mudam a forma da Page, não o dado. No simples, a Page tem seções em ordem fixa (painel, um gráfico e um parágrafo curto por argumento, contras, tabela de sinais, decisão, riscos e premissas, fontes) e sai rápida. No detalhado, o bot escolhe as seções, os gráficos e o tamanho, e a Page termina com `## Riscos e premissas` e `## Fontes`. Nos dois, todo número e toda série da Page saem do pacote de dados, e o fact_checker lê só o markdown da tese: o que existir só na Page não passa por ele. O chat fica curto nos dois.

O fact_checker aponta três tipos de erro: número diferente do pacote de dados (ou número de mercado, fundamento, projeção ou notícia recente que o pacote não traz), fato errado e texto incoerente com os próprios números. Conhecimento geral sem fonte, como uma regra de imposto, não é erro.

## Script

`skills/analista-v2-mercado/scripts/mercado.py` (Python 3 + `yfinance`). Três fontes, todas sem chave: `yfinance` para preço e opções, o SGS do Banco Central (`api.bcb.gov.br`) para Selic, CDI e IPCA, e o CSV do Tesouro Transparente para o Tesouro Direto. Saída JSON no stdout, em UTF-8 em qualquer sistema. Erro: objeto `{"erro": "...", "consultado_em": "..."}` e exit code diferente de zero. `consultado_em` é `America/Sao_Paulo`.

| Subcomando | Faz |
| --- | --- |
| `cotacao TICKER [TICKER…]` | preço, variação %, abertura, máxima, mínima, volume, moeda, nome curto (se houver), `data_pregao`, `fonte` `yfinance`, `atraso_estimado_min` 15. A saída é uma lista; item que falhou tem `erro` e o processo sai com código diferente de zero |
| `historico TICKER [--de YYYY-MM-DD] [--ate YYYY-MM-DD] [--intervalo 1d\|1w\|1m\|1h]` | OHLCV. Sem datas, 30 dias até hoje. `--ate` é inclusivo. MultiIndex do `yfinance` é achatado. Preço sem ajuste de provento |
| `opcoes SUBJACENTE [--vencimento YYYY-MM-DD] [--tipo CALL\|PUT] [--so-negociadas]` | cadeia do `yfinance` para subjacente dos EUA. `--so-negociadas` exige volume maior que zero |
| `taxa INDICADOR [INDICADOR…]` | `selic` (meta, série 432; efetiva anualizada, 1178), `cdi` (anualizado, 4389) e `ipca` (do mês, 433; acumulado em 12 meses, 13522). Cada valor é o último com data até hoje, numa janela de 100 dias: a meta Selic vem preenchida até a próxima reunião do Copom. `fonte` `bcb-sgs`. A saída é uma lista, como em `cotacao` |
| `tesouro [--tipo TEXTO]` | títulos do Tesouro Direto na data-base mais recente do CSV de preços e taxas do Tesouro Transparente: `vencimento`, `taxa_compra`, `taxa_venda`, `pu_compra`, `pu_venda`, e o campo `limitacao`, que diz que são as taxas da manhã. `--tipo` filtra por trecho do nome. O CSV traz o histórico inteiro (cerca de 15 MB) e o servidor não atende pedido de faixa: cada chamada baixa tudo. Coluna que falta no CSV sai como erro de formato. `fonte` `tesouro-transparente` |

Ticker B3 no formato de 4 letras e 1 ou 2 números (PETR4, BOVA11) ganha o sufixo `.SA`. Ticker dos EUA, índice (`^…`) e câmbio (`=X`) ficam como estão.

Download: `analista-v2-mercado` baixa o script da `stable` (`bots/analista-v2/skills/analista-v2-mercado/scripts/`) para um arquivo temporário e só troca `/workspace/analista-v2/mercado.py` se o arquivo baixado tiver a linha `# mercado.py`. Se o download falhar, a skill para sem usar a cópia do disco. Se faltar o pacote, a skill instala `yfinance` e, se a instalação falhar, para.

Limitações: o `yfinance` atrasa cerca de 15 minutos (não é tempo real) e não tem cadeia de opções da B3 (ticker `.SA` sai com erro no JSON). O Tesouro Direto sai com a taxa da manhã do dia útil anterior, e o JSON diz isso no campo `limitacao`. O script não traz curva de DI futuro nem taxa indicativa do mercado secundário de títulos públicos, e não estima esses dados.

## Testes

`python -m pytest bots/analista-v2/tests/test_analista_v2.py -q --import-mode=importlib`

Os testes mockam o `yfinance`, o Banco Central e o Tesouro Transparente e não acessam a rede. Os que executam o comando de download precisam de `bash` e `curl` e são pulados no Windows. `python scripts/check.py` na raiz inclui este arquivo.

## Manutenção

Criou, removeu ou renomeou skill, ou mudou a linha dela no `bot.md`? Rode `python scripts/gerar-ponteiros.py`.

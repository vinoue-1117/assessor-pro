# analista

Bot **Analista**: analista de mercado buy-side em pt-BR. Consulta preços com `yfinance` e taxas no Banco Central e no Tesouro Transparente, faz as contas em Python e entrega teses e comparações em Page depois de revisão adversarial.

Ficha do bot: [`bot.md`](bot.md).

## Instalar

Cole no chat deste bot. O mesmo prompt atualiza um bot já instalado. A conferência é pela função, não pelo nome nem pelo título do `bot.md`.

```
Atualize suas skills pelo repositório de bots, caminho analista, seguindo https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/bots/instalar.md.
Antes de começar, confira que você é o bot analista de mercado buy-side em pt-BR (seu nome pode ser outro). Se você for outro bot qualquer, pare e diga que este prompt é para outro bot.
Não apague nem altere nada em `/workspace/analista/`.
No fim, mostre a checklist do instalar.md marcada.
```

## Skills

| Skill | Quando |
| --- | --- |
| `analista-core` | sempre: persona, regras e entrega |
| `analista-mercado` | cotação, histórico, opções via `yfinance`, Selic, CDI e IPCA do Banco Central, taxa do Tesouro Direto, ou conta em Python |
| `analista-tese` | tese, comparação, relatório ou Page, com revisão adversarial antes de publicar |

O bot instalado guarda o ponteiro. A skill completa é baixada da branch `stable` a cada uso. Os ponteiros em `ponteiros/` são gerados por `python scripts/gerar-ponteiros.py`. Não edite essa pasta à mão.

Workspace deste bot: `/workspace/analista/` (o script de trabalho fica em `/workspace/analista/mercado.py`). Não use `/workspace/mercado/`.

## Script

`skills/analista-mercado/scripts/mercado.py` (Python 3 + `yfinance`). Três fontes, todas sem chave: `yfinance` para preço e opções, o SGS do Banco Central (`api.bcb.gov.br`) para Selic, CDI e IPCA, e o CSV do Tesouro Transparente para o Tesouro Direto. Saída JSON no stdout. Erro: objeto `{"erro": "...", "consultado_em": "..."}` e exit code diferente de zero. `consultado_em` é `America/Sao_Paulo`.

| Subcomando | Faz |
| --- | --- |
| `cotacao TICKER [TICKER…]` | preço, variação %, abertura, máxima, mínima, volume, moeda, nome curto (se houver), `data_pregao`, `fonte` `yfinance`, `atraso_estimado_min` 15. A saída é uma lista; item que falhou tem `erro` e o processo sai com código diferente de zero |
| `historico TICKER [--de YYYY-MM-DD] [--ate YYYY-MM-DD] [--intervalo 1d\|1w\|1m\|1h]` | OHLCV. Sem datas, 30 dias até hoje. `--ate` é inclusivo. MultiIndex do `yfinance` é achatado. Preço sem ajuste de provento |
| `opcoes SUBJACENTE [--vencimento YYYY-MM-DD] [--tipo CALL\|PUT] [--so-negociadas]` | cadeia do `yfinance` para subjacente dos EUA. `--so-negociadas` exige volume maior que zero |
| `taxa INDICADOR [INDICADOR…]` | `selic` (meta, série 432; efetiva anualizada, 1178), `cdi` (anualizado, 4389) e `ipca` (do mês, 433; acumulado em 12 meses, 13522). Cada valor é o último com data até hoje, numa janela de 100 dias: a meta Selic vem preenchida até a próxima reunião do Copom. `fonte` `bcb-sgs`. A saída é uma lista, como em `cotacao` |
| `tesouro [--tipo TEXTO]` | títulos do Tesouro Direto na data-base mais recente do CSV de preços e taxas do Tesouro Transparente: `vencimento`, `taxa_compra`, `taxa_venda`, `pu_compra`, `pu_venda`. `--tipo` filtra por trecho do nome. O CSV traz o histórico inteiro (cerca de 15 MB) e o servidor não atende pedido de faixa: cada chamada baixa tudo. Coluna que falta no CSV sai como erro de formato. `fonte` `tesouro-transparente` |

Ticker B3 no formato de 4 letras e 1 ou 2 números (PETR4, BOVA11) ganha o sufixo `.SA`. Ticker dos EUA, índice (`^…`) e câmbio (`=X`) ficam como estão.

Download: `analista-mercado` baixa o script da `stable` (`bots/analista/skills/analista-mercado/scripts/`) para um arquivo temporário e só troca `/workspace/analista/mercado.py` se a 1ª linha for `# mercado.py v<N>` com N igual ou maior que `skills/analista-mercado/scripts/versao-minima`. Se o download falhar ou a versão for menor, a skill para sem usar a cópia do disco. Se faltar o pacote, a skill instala `yfinance` e, se a instalação falhar, para.

Limitações: o `yfinance` atrasa cerca de 15 minutos (não é tempo real) e não tem cadeia de opções da B3 (ticker `.SA` sai com erro no JSON). O Tesouro Direto sai com a taxa da manhã do dia útil anterior. O script não traz curva de DI futuro nem taxa indicativa do mercado secundário de títulos públicos, e não estima esses dados.

## Testes

`python -m pytest bots/analista/tests/test_analista.py -q --import-mode=importlib`

Os testes mockam o `yfinance`, o Banco Central e o Tesouro Transparente e não acessam a rede. Os que executam o comando de download precisam de `bash` e `curl` e são pulados no Windows. `python scripts/check.py` na raiz inclui este arquivo.

## Evals

`evals/revisor/` compara dois papéis de revisor sobre os mesmos rascunhos de tese e o mesmo pacote de dados: o advogado do diabo, lido da seção 3 da `analista-tese`, e o conferente factual de `papel-conferente.md`. Os rascunhos e o pacote (`dados.json`) têm valor fictício em tudo.

| Rascunho | Conteúdo | Gabarito | Casos |
| --- | --- | --- | --- |
| `rascunho.md` | seis erros plantados e seis frases corretas | `gabarito.json` | `advogado`, `conferente` |
| `rascunho-limpo.md` | o mesmo texto com os seis erros corrigidos | `gabarito-limpo.json` | `advogado-limpo`, `conferente-limpo` |

Os critérios do juiz ficam em `graders/`. O gabarito de cada rascunho lista os critérios que valem para ele e o trecho que cada um confere.

`python bots/analista/evals/revisor/rodar.py`

O script monta os quatro casos numa pasta temporária, fora do repositório, e roda `claude plugin eval` pelo login do plano, com cinco execuções por caso e Sonnet no revisor e no juiz. `--caso` roda só os casos que casam com o glob (`--caso "*-limpo"`). Ele não usa shell e roda no Windows. O revisor roda em Claude, não no modelo do bot: o resultado compara os papéis, não mede o bot.

Na pasta temporária ficam o relatório de entrada (`entrada.html`: os papéis, cada rascunho com os trechos do gabarito marcados e os critérios dele, e o JSON), o resultado (`aggregate-result.json`), o relatório de saída do comando (`relatorio.html`) e as respostas (`respostas/`). `--so-entrada` grava só o relatório de entrada, sem rodar o eval.

| Contagem | De onde sai |
| --- | --- |
| erros plantados pegos | critérios `erro-*` que passaram |
| frases corretas contestadas | critérios `correta-*` que reprovaram. Conta quando o revisor diz que o número está errado ou sem base; levantar risco em torno dele não conta |
| execuções em que o revisor aprovou a tese | critério `aprova`, só no rascunho sem erro: veredito `sólida` ou resultado `confere` |
| afirmações que não estão no rascunho nem no JSON | contagem à mão, lendo `respostas/`. O juiz do comando só vê a resposta e o critério, e reprova resposta que não traz fato de fora |

O script imprime a média, o mínimo e o máximo das duas primeiras contagens por caso, as aprovações e a linha de veredito de cada execução.

Mudou um rascunho ou o pacote? Mude o critério em `graders/` e o trecho no gabarito no mesmo diff. O prefixo do nome do critério (`erro-`, `correta-`) decide em qual contagem ele entra.

## Manutenção

Mudou o comportamento que a skill espera do `mercado.py`? Suba o número na 1ª linha (`# mercado.py vN`) e o mesmo número em `scripts/versao-minima`, no mesmo diff. Criou, removeu ou renomeou skill, ou mudou a linha dela no `bot.md`? Rode `python scripts/gerar-ponteiros.py`.

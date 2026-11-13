---
name: analista-mercado
description: 'Use sempre que precisar de cotação, histórico de preços ou cadeia de opções via yfinance, de Selic, CDI ou IPCA do Banco Central, de taxa do Tesouro Direto, ou conferir números em Python.'
---

# Mercado

Consulta de preço, histórico e opções via `yfinance`, de Selic, CDI e IPCA pelo Banco Central e de taxa do Tesouro Direto pelo Tesouro Transparente. Todo número de mercado vem de uma chamada feita na hora. Se a chamada falhar, pare e diga que o dado não veio. Não invente cotação, volume, cadeia ou taxa.

## Script

Baixe a cada execução, da branch `stable`, para um arquivo temporário. Não procure o script ao lado desta skill: o bot instalado tem só o ponteiro. Só troque `/workspace/analista/mercado.py` se o download der certo e a versão da 1ª linha for igual ou maior que a de `versao-minima`. Se falhar, pare e avise. Não use a cópia do disco.

`b=https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/bots/analista/skills/analista-mercado/scripts; t=$(mktemp) && mkdir -p /workspace/analista && min=$(curl -fsSL "$b/versao-minima") && curl -fsSL "$b/mercado.py" -o "$t" && v=$(grep -m1 -o '^# mercado.py v[0-9][0-9]*' "$t" | grep -o '[0-9][0-9]*$') && [ "$min" -ge 1 ] && [ "$v" -ge "$min" ] && mv "$t" /workspace/analista/mercado.py || { rm -f "$t" 2>/dev/null || true; echo "Falha ao baixar o mercado.py (exige v${min:-?} ou maior). Pare e não use a cópia do disco."; exit 1; }`

Não edite o script.

Se faltar o pacote: `python3 -c "import yfinance" 2>/dev/null || python3 -m pip install -q yfinance`. Se a instalação falhar, pare e avise. Não troque a fonte.

Rode `python3 /workspace/analista/mercado.py …`. A saída é JSON no stdout. Erro de comando: um objeto `{"erro": "...", "consultado_em": "..."}` e exit code diferente de zero. Em `cotacao` e `taxa`, a saída é uma lista; o item que falhou tem `erro` e `consultado_em`, e o exit code é diferente de zero se algum item falhou.

## Comandos

- `cotacao TICKER [TICKER…]`: preço, variação %, abertura, máxima, mínima, volume, moeda, nome curto (se o `yfinance` trouxer), `data_pregao`, `fonte` (`yfinance`), `atraso_estimado_min` (15) e `consultado_em` (`America/Sao_Paulo`).
- `historico TICKER [--de YYYY-MM-DD] [--ate YYYY-MM-DD] [--intervalo 1d|1w|1m|1h]`: OHLCV. Sem datas, os 30 dias até hoje em `America/Sao_Paulo`. O intervalo `1w` e `1m` saem como semana e mês. O preço não vem ajustado por provento. Se um salto parecer split ou agrupamento, diga isso em vez de tratar o salto como retorno.
- `opcoes SUBJACENTE [--vencimento YYYY-MM-DD] [--tipo CALL|PUT] [--so-negociadas]`: cadeia do `yfinance`. Funciona para subjacente dos EUA. Sem `--vencimento`, vem só o primeiro vencimento da cadeia; os outros estão em `vencimentos_disponiveis`. Vencimento que não existe sai com erro e a lista dos disponíveis. `--so-negociadas` fica só com volume maior que zero.
- `taxa INDICADOR [INDICADOR…]`: `selic` (`meta` e `efetiva`), `cdi` (`taxa`) e `ipca` (`mes` e `acumulado_12m`), pelo SGS do Banco Central. Cada valor vem com `unidade`, `data` e `serie_sgs`, e a `fonte` é `bcb-sgs`. A `data` é o dia a que o valor se refere; no IPCA, o primeiro dia do mês de referência.
- `tesouro [--tipo TEXTO]`: os títulos do Tesouro Direto na data-base mais recente (`data_base`, em geral o dia útil anterior), com `vencimento`, `taxa_compra`, `taxa_venda`, `pu_compra` e `pu_venda`; a `fonte` é `tesouro-transparente`. `taxa_compra` e `pu_compra` valem para quem compra o título; `taxa_venda` e `pu_venda`, para quem revende ao Tesouro antes do vencimento. `--tipo` filtra por trecho do nome (`ipca+`, `prefixado`, `selic`, `renda+`). O nome separa o título que paga juros semestrais (`com Juros Semestrais`) do que paga tudo no vencimento, e os dois podem ter o mesmo vencimento: escolha a linha pelo nome inteiro e pelo `vencimento`. A lista inclui título que não está mais à venda e não tem campo que diga qual está aberto para compra: se a resposta depender disso, diga que não foi conferido. A taxa é em % a.a. e muda de sentido com o título: nominal no Prefixado, juro real acima do índice no IPCA+, Educa+, Renda+ e IGPM+, e ágio sobre a Selic no Tesouro Selic. São as taxas da manhã do Tesouro Direto, não a taxa indicativa do mercado secundário. A chamada baixa cerca de 15 MB e leva alguns segundos: rode uma vez e filtre o JSON.

Ticker B3 de 4 letras e 1 ou 2 números (PETR4, BOVA11) vira `.SA`. Ticker dos EUA, índice (`^…`) e câmbio (`=X`) ficam como estão.

## Regras

- Todo número publicado traz a `fonte` da chamada (`yfinance`, `bcb-sgs` ou `tesouro-transparente`) e `consultado_em` (`America/Sao_Paulo`) da chamada desta vez. Não reaproveite JSON de outra conversa.
- Quando o atraso mudar a decisão (preço de agora, execução, stop), avise que o `yfinance` atrasa cerca de 15 minutos.
- Se o comando sair com `erro` ou exit code diferente de zero, pare essa parte e diga que o dado não veio. Não complete com memória, com busca web nem com outra fonte.
- Opções da B3, curva de DI futuro e taxa indicativa do mercado secundário de títulos públicos não vêm por este script. `opcoes` em ticker `.SA` devolve erro no JSON: repasse o erro e pare essa parte. Se o dono pedir um desses dados, avise que o script não traz e não estime.
- Conta (variação, múltiplo, assimetria, tamanho, spread) é feita em Python, com o JSON da chamada como entrada. Múltiplo usa também o número de fundamento lido na web, com a página e a data. Não faça a conta de cabeça e não arredonde para a conta fechar.
- Fundamentos, projeção, resultado recente e notícia: use a busca e a leitura web nativas deste bot. Em análise de empresa, confira a data do último trimestre divulgado. Em ativo com ticker no `yfinance`, rode `historico` da última semana antes de concluir. `tesouro` e `taxa` trazem só o valor mais recente: nesses casos, diga que a variação da última semana não foi conferida. Se a busca não achar a data ou o documento, diga que não achou. Não preencha o buraco.

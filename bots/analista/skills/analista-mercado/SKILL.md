---
name: analista-mercado
description: 'Use sempre que precisar de cotação, histórico de preços ou cadeia de opções via yfinance, ou conferir números em Python.'
---

# Mercado

Consulta de preço, histórico e opções via `yfinance`. Todo número de mercado vem de uma chamada feita na hora. Se a chamada falhar, pare e diga que o dado não veio. Não invente cotação, volume, cadeia ou taxa.

## Script

Baixe a cada execução, da branch `stable`, para um arquivo temporário. Não procure o script ao lado desta skill: o bot instalado tem só o ponteiro. Só troque `/workspace/analista/mercado.py` se o download der certo e a versão da 1ª linha for igual ou maior que a de `versao-minima`. Se falhar, pare e avise. Não use a cópia do disco.

`b=https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/bots/analista/skills/analista-mercado/scripts; t=$(mktemp) && mkdir -p /workspace/analista && min=$(curl -fsSL "$b/versao-minima") && curl -fsSL "$b/mercado.py" -o "$t" && v=$(grep -m1 -o '^# mercado.py v[0-9][0-9]*' "$t" | grep -o '[0-9][0-9]*$') && [ "$min" -ge 1 ] && [ "$v" -ge "$min" ] && mv "$t" /workspace/analista/mercado.py || { rm -f "$t" 2>/dev/null || true; echo "Falha ao baixar o mercado.py (exige v${min:-?} ou maior). Pare e não use a cópia do disco."; exit 1; }`

Se o comando falhar, pare e avise. Não use a cópia do disco. Não edite o script.

Se faltar o pacote: `python3 -c "import yfinance" 2>/dev/null || python3 -m pip install -q yfinance`. Se a instalação falhar, pare e avise. Não troque a fonte.

Rode `python3 /workspace/analista/mercado.py …`. A saída é JSON no stdout. Erro de comando: um objeto `{"erro": "...", "consultado_em": "..."}` e exit code diferente de zero. Em `cotacao`, a saída é uma lista; o item que falhou tem `erro` e `consultado_em`, e o exit code é diferente de zero se algum ticker falhou.

## Comandos

- `cotacao TICKER [TICKER…]`: preço, variação %, abertura, máxima, mínima, volume, moeda, nome curto (se o `yfinance` trouxer), `data_pregao`, `fonte` (`yfinance`), `atraso_estimado_min` (15) e `consultado_em` (`America/Sao_Paulo`).
- `historico TICKER [--de YYYY-MM-DD] [--ate YYYY-MM-DD] [--intervalo 1d|1w|1m|1h]`: OHLCV. Sem datas, os 30 dias até hoje em `America/Sao_Paulo`. O intervalo `1w` e `1m` saem como semana e mês. O preço não vem ajustado por provento. Se um salto parecer split ou agrupamento, diga isso em vez de tratar o salto como retorno.
- `opcoes SUBJACENTE [--vencimento YYYY-MM-DD] [--tipo CALL|PUT] [--so-negociadas]`: cadeia do `yfinance`. Funciona para subjacente dos EUA. `--so-negociadas` fica só com volume maior que zero.

Ticker B3 de 4 letras e 1 ou 2 números (PETR4, BOVA11) vira `.SA`. Ticker dos EUA, índice (`^…`) e câmbio (`=X`) ficam como estão.

## Regras

- Todo número publicado traz `fonte` (`yfinance`) e `consultado_em` (`America/Sao_Paulo`) da chamada desta vez. Não reaproveite JSON de outra conversa.
- Quando o atraso mudar a decisão (preço de agora, execução, stop), avise que o `yfinance` atrasa cerca de 15 minutos.
- Se o comando sair com `erro` ou exit code diferente de zero, pare essa parte e diga que o dado não veio. Não complete com memória, com busca web nem com outra fonte.
- Opções da B3 e taxas DI ou SELIC não vêm pelo `yfinance`. `opcoes` em ticker `.SA` devolve erro no JSON: repasse o erro e pare essa parte. Se o dono pedir DI, SELIC ou a cadeia da B3, avise que esta fonte não traz e não estime.
- Conta (variação, múltiplo, assimetria, tamanho, spread) é feita em Python, com o JSON da chamada como entrada. Não faça a conta de cabeça e não arredonde para a conta fechar.
- Fundamentos, resultado recente e notícia: use a busca e a leitura web nativas deste bot. Confira a data do último trimestre divulgado. Rode `historico` da última semana antes de concluir. Se a busca não achar a data ou o documento, diga que não achou. Não preencha o buraco.

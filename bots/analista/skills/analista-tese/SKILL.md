---
name: analista-tese
description: 'Use quando o pedido envolver tese, comparação, relatório ou estrutura em Page, com contras e conferência dos números antes de publicar.'
---

# Tese

Tese, comparação, relatório ou análise aprofundada sai como Page em pt-BR, com as seções e a ordem da seção 5. Antes de publicar, dois subagentes leem a tese: o antagonista procura contras e riscos no rascunho, e o conferente confere o texto final contra o pacote de dados.

Número de mercado só entra se `analista-mercado` tiver trazido o JSON nesta conversa. Conta em Python, não de cabeça. Siga a persona de `analista-core`.

## 1. Dados

Siga `analista-mercado`: baixe o `mercado.py` com o comando de lá e rode a chamada que o pedido exige. Não use cópia antiga do disco.

Grave o pacote em `/tmp/analista-dados-<slug>.json` com `json.dump` em Python. Não monte esse JSON à mão. `<slug>` é o assunto em minúsculas, só `[a-z0-9-]`.

```json
{
  "mercado": [],
  "web": [{"titulo": "", "url": "", "data": "", "numeros": {}}],
  "contas": {}
}
```

- `mercado`: o JSON do script, sem editar número.
- `web`: só página que você abriu de fato, com a data do documento ou da publicação. Número de fundamento ou de projeção que a tese usa (lucro, receita, dívida, expectativa do boletim Focus) entra em `numeros` como está no documento, com a unidade e o período. Fundamento, projeção, resultado recente e notícia vêm da busca e da leitura web nativas deste bot. Em tese sobre empresa, confira a data do último trimestre divulgado. Em tese sobre ativo com ticker no `yfinance`, rode `historico` da última semana antes de concluir. Em tese sobre Tesouro Direto ou taxa, o script só traz o valor mais recente: registre em `Riscos, limitações e premissas` que a variação da última semana não foi conferida.
- `contas`: o que o Python imprimiu a partir de `mercado` e dos `numeros` de `web` (variação, múltiplo, assimetria, tamanho). Se a conta não sair do script, não entre na tese.

## 2. Rascunho

Escreva `/tmp/analista-rascunho-<slug>.md` em markdown, já nas seções da Page (seção 5). O rascunho traz a decisão de alocação, a assimetria de upside contra downside, o tamanho sugerido, o catalisador, o horizonte e o que faria mudar de ideia. Cada número rastreável ao JSON.

## 3. Antagonista

Rode um subagente `knowledgeWork` pela ferramenta `Task`, com `subagent_type` `knowledgeWork`. Esse subagente começa sem o histórico da conversa. Passe somente:

- o rascunho;
- o JSON de `/tmp/analista-dados-<slug>.json`;
- o papel: antagonista. Procurar contras e riscos da tese. Devolver uma lista de itens, cada um destinado a uma seção: `Contras`, `Riscos` ou `O que faria mudar de ideia`. Apoiar cada item num dado do pacote, citando o dado, ou marcar o item como hipótese. Agrupar os itens sob o nome da seção de destino, uma linha por item; o item apoiado em dado termina com o dado entre parênteses, e o item sem dado começa com `Hipótese:`. Não dar veredito, não dizer se a tese pode ser publicada e não reescrever a tese.

Uma passada só. Não passe o chat nem a memória. Se a chamada falhar ou voltar vazia, pare e diga ao dono que a revisão não rodou, e não publique. Se o antagonista disser que não achou contra nem risco, siga sem itens.

## 4. Texto final e conferência

Escreva `/tmp/analista-tese-<slug>.md`: o rascunho com os itens do antagonista nas seções de destino.

| Bloco do antagonista | Seção da Page |
| --- | --- |
| `Contras` | `## Contras` |
| `Riscos` | `## Riscos, limitações e premissas` |
| `O que faria mudar de ideia` | `## Decisão` |

O item entra só na seção de destino, como veio: o dado entre parênteses no fim, ou `Hipótese:` no começo. Não reescreva o resto da tese por causa dele. Item de risco ou de gatilho com limite numérico ganha também uma linha na tabela de sinais.

Antes de levar os itens:

- Item que aponta erro do rascunho ("o texto diz X, o pacote traz Y") é correção, não item: corrija o trecho do rascunho, rode de novo a conta que mudar e não leve o item para a Page.
- Número de item que não está em `mercado`, nos `numeros` de `web` nem em `contas`: rode a conta em Python e grave o resultado em `contas`. Se a conta não sair do script, tire o número; o resto do item entra como `Hipótese:` ou sai.
- Modo padrão: até três itens por seção. Se vierem mais, fique primeiro com os apoiados em dado e, entre eles, com os que mais mexem na decisão.
- Modo rigoroso: sem teto de itens. Vale quando o dono pede análise mais funda ou mais rigor, com as palavras que forem.

Rode outro subagente `knowledgeWork`, também sem o histórico da conversa. Passe somente:

- o texto final;
- o JSON de `/tmp/analista-dados-<slug>.json`;
- o papel: conferente factual. Conferir se cada número do texto bate com `mercado`, com os `numeros` de `web` ou com `contas`. Conferir se cada afirmação de fato tem dado no pacote. Conferir se o texto é coerente com os próprios números (gatilho, linha de corte). Devolver a lista de divergências, cada uma com o trecho e o valor certo do pacote, e o resultado `confere` ou `reescrever`. Não opinar sobre a qualidade da tese e não reescrever a tese.

Não passe o chat, a memória, o rascunho nem a resposta do antagonista. Se o conferente não devolver `confere` ou `reescrever`, pare e diga ao dono que a conferência não rodou. Não invente resultado e não publique.

- `confere`: publique (seção 5).
- `reescrever`: corrija os trechos apontados, rode de novo a conta que mudar e passe o texto final inteiro a um novo conferente, com o mesmo papel. São duas conferências no máximo. Se a segunda devolver `reescrever`, não publique: diga ao dono no chat que a tese não passou na conferência e liste cada divergência que ficou, com o trecho e o valor do pacote.

A Page publica o texto que a última conferência leu. Não mude número, gatilho nem conclusão depois dela.

## 5. Page

Publique a Page com a skill `canvas`, pela ferramenta `WriteCanvas`, montada a partir do texto final conferido. A skill `canvas` escolhe o componente de cada seção. Painel, gráfico e tabela só usam número que está no texto final. Se a Page não publicar, pare e diga ao dono qual foi o erro. Não cole a tese no chat.

A Page tem estas seções, nesta ordem:

1. Painel de indicadores: a decisão de alocação (lado, tamanho sugerido, horizonte) e os números que sustentam a tese, cada um com valor e data. Uma frase com a decisão vem antes do painel.
2. Uma seção por argumento, com um gráfico dos dados dele e um parágrafo curto que diz o que o gráfico mostra para a decisão. O gráfico só entra se o pacote de dados tiver uma série ou valores para comparar: `tesouro` e `taxa` trazem só o valor mais recente. Sem isso, o argumento sai com o parágrafo e os números.
3. `## Contras`: os itens do antagonista.
4. Tabela de sinais: cada catalisador, risco e gatilho de invalidação numa linha, com o valor de hoje, o limite e o status (verde: a favor; amarelo: a acompanhar; vermelho: contra). A cor fica só na palavra do status.
5. `## Riscos, limitações e premissas`.
6. `## Decisão`, em destaque: lado, tamanho sugerido, horizonte e o que faria mudar de ideia.
7. Uma seção `## Fontes` com fonte, data e horário de cada número e de cada documento.

Seção sem conteúdo sai da Page. Pedido sem decisão de alocação (um relatório, uma comparação sem recomendação) sai sem o painel e sem `## Decisão`.

As respostas do antagonista e do conferente são material de trabalho e ficam fora da Page: nada de resultado da conferência, seção de resposta à revisão ou ressalva espalhada pelos parágrafos.

## 6. Chat

Entregue o link da Page e a decisão de alocação (lado, tamanho sugerido, horizonte), curta. Se restou limitação de dado ou ressalva importante, uma linha curta a mais. Se o modo rigoroso rodou, diga isso nessa linha. Sem ressalva e sem o modo rigoroso, não acrescente linha. Não cole o rascunho nem a crítica no chat.

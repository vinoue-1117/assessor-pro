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
- `contas`: o que o Python imprimiu a partir de `mercado` e dos `numeros` de `web` (variação, múltiplo, assimetria, tamanho). Se a conta não sair do script, não entre na tese. Dado que o dono deu nesta conversa (valor, carteira, limite de perda, prazo) também entra em `contas`, como ele deu, com a chave `origem_<nome>` valendo `"informado pelo dono"`.

## 2. Rascunho

Escreva `/tmp/analista-rascunho-<slug>.md` em markdown, já nas seções da Page (seção 5). O rascunho traz a decisão de alocação, a assimetria de upside contra downside, o tamanho sugerido, o catalisador, o horizonte e o que faria mudar de ideia. Em pedido sem decisão de alocação, ele fica sem a decisão, a assimetria, o tamanho sugerido, o catalisador, o horizonte e o que faria mudar de ideia. Cada número rastreável ao JSON.

- Tamanho sugerido: sai de conta em `contas`, a partir do valor, da carteira ou do limite de perda que o dono deu nesta conversa. Sem esse dado, não escolha tamanho nem divisão: escreva que o tamanho não foi calculado e qual dado falta.
- Assimetria: o ganho no cenário a favor contra a perda no cenário contrário, os dois com chave em `contas`.
- Catalisador: o evento ou dado que faz a tese andar. Se não houver, escreva que não há.

## 3. Antagonista

Rode um subagente `knowledgeWork` pela ferramenta `Task`, com `subagent_type` `knowledgeWork`. Esse subagente começa sem o histórico da conversa. Passe somente:

- o rascunho;
- o JSON de `/tmp/analista-dados-<slug>.json`;
- o papel: antagonista. Procurar contras e riscos da tese. Devolver uma lista de itens, cada um destinado a uma seção: `Contras`, `Riscos` ou `O que faria mudar de ideia`. Apoiar cada item num dado do pacote, citando o dado, ou marcar o item como hipótese. Agrupar os itens sob o nome da seção de destino, uma linha por item; o item apoiado em dado termina com o dado entre parênteses, e o item sem dado começa com `Hipótese:`. Não dar veredito, não dizer se a tese pode ser publicada e não reescrever a tese.

Uma passada só. Não passe o chat nem a memória. Se a chamada falhar ou voltar vazia, pare e diga ao dono que a revisão não rodou, e não publique. Se o antagonista disser que não achou contra nem risco, siga sem itens.

Grave a resposta inteira, como veio, em `/tmp/analista-antagonista-<slug>.md`. Não resuma nem edite.

## 4. Texto final e conferência

O texto final, `/tmp/analista-tese-<slug>.md`, é o rascunho com os itens escolhidos nas seções de destino. Quem grava o texto final é o `mercado.py itens`, mesmo sem item. Não digite item à mão nem edite o texto final: toda mudança é feita no rascunho, e o passo 5 roda de novo.

| Bloco do antagonista | Seção da Page |
| --- | --- |
| `Contras` | `## Contras` |
| `Riscos` | `## Riscos, limitações e premissas` |
| `O que faria mudar de ideia` | `## Decisão`; em pedido sem decisão de alocação, `## Riscos, limitações e premissas` |

1. `python3 /workspace/analista/mercado.py itens /tmp/analista-antagonista-<slug>.md` lista os itens numerados (`n`, `bloco` e `linha`) e, em `ignoradas`, as linhas fora dos três blocos. Se a resposta trouxer contra ou risco que não veio em `itens`, pare e diga ao dono que a revisão não pôde ser lida.
2. Item que aponta erro do rascunho ("o texto diz X, o pacote traz Y") é correção, não item: corrija o trecho do rascunho, rode de novo a conta que mudar e deixe o item de fora.
3. Número de item que não está em `mercado`, nos `numeros` de `web` nem em `contas`: rode a conta em Python e grave o resultado em `contas`. Se a conta não sair do script, o item fica de fora.
4. Escolha os itens; nenhum é escolha válida. Modo padrão: até três por seção, primeiro os apoiados em dado e, entre eles, os que mais mexem na decisão. Modo rigoroso, quando o dono pede análise mais funda ou mais rigor, com as palavras que forem: sem teto. Item cujo dado entre parênteses não sustenta a afirmação vai como hipótese ou fica de fora. Item de risco ou de gatilho escolhido que tem limite numérico ganha uma linha na tabela de sinais do rascunho.
5. `python3 /workspace/analista/mercado.py itens /tmp/analista-antagonista-<slug>.md --rascunho /tmp/analista-rascunho-<slug>.md --saida /tmp/analista-tese-<slug>.md --levar <n,n> --hipotese <n>`. `--levar` copia a linha como veio; `--hipotese` tira o dado do fim e põe `Hipótese:` no começo. O item que não está em nenhuma das duas fica de fora; sem as duas, o texto final é o rascunho. Se o script devolver erro, corrija a chamada ou a seção que falta no rascunho e rode de novo.

Não reescreva o resto da tese por causa de um item.

Rode outro subagente `knowledgeWork`, também sem o histórico da conversa. Passe somente:

- o texto final;
- o JSON de `/tmp/analista-dados-<slug>.json`;
- as mensagens do dono, como ele escreveu: o pedido e cada mensagem de onde saiu um dado `origem_*`;
- o papel: conferente factual. Conferir se cada número do texto bate com `mercado`, com os `numeros` de `web` ou com `contas`. Conferir se cada afirmação de fato tem dado no pacote. Conferir se o texto é coerente com os próprios números (gatilho, linha de corte). Número que não está em `mercado`, nos `numeros` de `web` nem em `contas` é divergência, mesmo que a conta feche com dados do pacote. Afirmação de fato sem dado no pacote é divergência, mesmo que pareça razoável. Item que começa com `Hipótese:` não é divergência, a não ser que traga número que não está no pacote. Conferir cada chave `origem_*` com `"informado pelo dono"` contra as mensagens do dono: dado que elas não trazem é divergência. Devolver a lista de divergências, cada uma com o trecho e o valor certo do pacote, e o resultado `confere` ou `reescrever`. Não opinar sobre a qualidade da tese e não reescrever a tese.

Além dessas mensagens, não passe o resto do chat, a memória, o rascunho nem a resposta do antagonista. Se o conferente não devolver `confere` ou `reescrever`, pare e diga ao dono que a conferência não rodou. Não invente resultado e não publique.

- `confere`: publique (seção 5).
- `reescrever`: corrija no rascunho os trechos apontados, rode de novo a conta que mudar e o passo 5, e passe o texto final inteiro a um novo conferente, com o mesmo papel. Trecho apontado numa linha de item não se corrige: o item sai da escolha. Vai em `--hipotese` só quando o trecho apontado é o dado entre parênteses do fim, que o `--hipotese` tira. São duas conferências no máximo. Se a segunda devolver `reescrever`, não publique: diga ao dono no chat que a tese não passou na conferência e liste cada divergência que ficou, com o trecho e o valor do pacote. O chat leva só isso: da tese, só os trechos das divergências; sem a decisão, as ressalvas e os outros números, e sem oferecer outra conferência. Se o dono pedir a tese de novo, ela recomeça da seção 1.

A Page publica o texto que a última conferência leu. Não mude número, gatilho nem conclusão depois dela.

## 5. Page

Publique a Page com a skill `canvas`, pela ferramenta `WriteCanvas`, montada a partir do texto final conferido. A skill `canvas` escolhe o componente de cada seção. Painel e tabela só usam número que está no texto final. O gráfico usa a série do pacote de dados, sem ponto de fora dele. Se a Page não publicar, pare e diga ao dono qual foi o erro. Não cole a tese no chat.

A Page tem estas seções, nesta ordem:

1. Painel de indicadores: a decisão de alocação (lado, tamanho sugerido, horizonte) e os números que sustentam a tese, cada um com valor e data. Uma frase com a decisão vem antes do painel.
2. Uma seção por argumento, com um gráfico dos dados dele e um parágrafo curto que diz o que o gráfico mostra para a decisão. O gráfico só entra se o pacote de dados tiver uma série ou valores para comparar: `tesouro` e `taxa` trazem só o valor mais recente. Sem isso, o argumento sai com o parágrafo e os números.
3. `## Contras`: os itens do antagonista.
4. Tabela de sinais: cada catalisador, risco e gatilho de invalidação numa linha, com o valor de hoje, o limite e o status (verde: a favor; amarelo: a acompanhar; vermelho: contra). A cor fica só na palavra do status.
5. `## Riscos, limitações e premissas`.
6. `## Decisão`, em destaque: lado, tamanho sugerido, horizonte, assimetria, catalisador e o que faria mudar de ideia.
7. Uma seção `## Fontes` com fonte, data e horário de cada número e de cada documento.

Seção sem conteúdo sai da Page. Pedido sem decisão de alocação (um relatório, uma comparação sem recomendação) sai sem o painel e sem `## Decisão`, e os itens de `O que faria mudar de ideia` vão para `## Riscos, limitações e premissas`.

As respostas do antagonista e do conferente são material de trabalho e ficam fora da Page: nada de resultado da conferência, seção de resposta à revisão ou ressalva espalhada pelos parágrafos.

## 6. Chat

Entregue o link da Page e a decisão de alocação (lado, tamanho sugerido, horizonte), curta. Se restou limitação de dado ou ressalva importante, uma linha curta a mais. Se o modo rigoroso rodou, diga isso nessa linha. Sem ressalva e sem o modo rigoroso, não acrescente linha. Não cole o rascunho nem a crítica no chat.

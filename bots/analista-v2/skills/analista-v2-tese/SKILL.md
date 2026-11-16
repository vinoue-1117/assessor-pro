---
name: analista-v2-tese
description: 'Analista v2: use quando o pedido envolver tese, comparação, relatório ou estrutura em Page. Uma conferência de fatos e a Page é publicada.'
---

# Tese

Tese, comparação, relatório ou análise aprofundada sai como Page em pt-BR, com as seções e a ordem da seção 5. O caminho é: dados, tese, uma conferência de fatos, tese final, Page. Com o dado principal em mãos, todo pedido termina em Page publicada: a conferência corrige a tese e não decide se ela sai.

O dono está esperando. Faça cada passo uma vez, você mesmo: refazer uma conta na tese final e republicar a Page depois de erro de compilação fazem parte do passo. O único subagente desta skill é o fact_checker da seção 3, chamado uma vez: não passe dados, escrita, correção nem a Page a outro subagente, e não rode outro revisor nem uma segunda conferência.

Número de mercado só entra se `analista-v2-mercado` tiver trazido o JSON nesta conversa. Conta em Python, não de cabeça. Siga a persona de `analista-v2-core`.

## 1. Dados

Siga `analista-v2-mercado`: baixe o `mercado.py` com o comando de lá e rode a chamada que o pedido exige. Não use cópia antiga do disco.

Dado principal é o número de que a decisão depende: a cotação ou a taxa do ativo da tese. Se ele não vier, pare agora e diga ao dono qual dado não veio. Outro dado que não veio (um fundamento, uma notícia, uma série) não para a tese: siga sem ele, e a falta vai para a linha do chat (seção 6).

Grave o pacote em `/tmp/analista-v2-dados-<slug>.json` com `json.dump` em Python. Não monte esse JSON à mão. `<slug>` é o assunto em minúsculas, só `[a-z0-9-]`.

```json
{
  "mercado": [],
  "web": [{"titulo": "", "url": "", "data": "", "numeros": {}}],
  "contas": {}
}
```

- `mercado`: o JSON do script, sem editar número.
- `web`: só página que você abriu de fato, com a data do documento ou da publicação. Abra as páginas de que a decisão depende, não todas as que a busca trouxer. Número de fundamento ou de projeção que a tese usa (lucro, receita, dívida, expectativa do boletim Focus) entra em `numeros` como está no documento, com a unidade e o período. Fundamento, projeção, resultado recente e notícia vêm da busca e da leitura web nativas deste bot. Em tese sobre empresa, confira a data do último trimestre divulgado. Em tese sobre ativo com ticker no `yfinance`, rode `historico` da última semana antes de concluir. Em tese sobre Tesouro Direto ou taxa, o script só traz o valor mais recente: a variação da última semana fica sem conferir, e isso vai para a linha do chat (seção 6).
- `contas`: o que o Python imprimiu a partir de `mercado` e dos `numeros` de `web` (variação, múltiplo, assimetria). Dado que o dono deu nesta conversa e que a tese usa (o prazo, por exemplo) também entra em `contas`, como ele deu, com a chave `origem_<nome>` valendo `"informado pelo dono"`.

Conhecimento geral e estável (regra de imposto, como o título paga) não pede página aberta e não entra no pacote.

## 2. Tese

Escreva `/tmp/analista-v2-tese-<slug>.md` em markdown, já nas seções da Page (seção 5). A tese traz a decisão de alocação, a assimetria de upside contra downside, o catalisador, o horizonte e o que faria mudar de ideia. Pedido sem decisão de alocação (um relatório, uma comparação sem recomendação) fica sem a decisão, a assimetria, o catalisador e o horizonte; o que faria mudar de ideia vai para `Riscos e premissas`.

- Assimetria: o ganho no cenário a favor contra a perda no cenário contrário, os dois com chave em `contas`.
- Catalisador: o evento ou dado que faz a tese andar. Se não houver, escreva que não há.
- Contras e riscos: você mesmo escreve. `## Contras` traz o que pesa contra a decisão; `## Riscos e premissas`, o que pode dar errado e as premissas de que a decisão depende, com a ressalva sobre o que um número é; `## Decisão`, o que faria mudar de ideia. Em cada uma, só os itens que mexem na decisão, do que mais pesa para o que menos pesa. Risco ou gatilho com limite numérico ganha uma linha na tabela de sinais.

## 3. Conferência de fatos

Rode um subagente `knowledgeWork` pela ferramenta `Task`, com `subagent_type` `knowledgeWork`. Esse subagente começa sem o histórico da conversa. Passe somente:

- a tese;
- o JSON de `/tmp/analista-v2-dados-<slug>.json`;
- as mensagens do dono, como ele escreveu: o pedido e cada mensagem de onde saiu um dado `origem_*`;
- o papel: fact_checker. Apontar só o que está errado na tese. Há três tipos de erro. Tipo 1, número diferente do pacote: cotação, taxa de juros, índice, fundamento de empresa, projeção ou resultado de conta que o texto traz com valor diferente do que está em `mercado`, nos `numeros` de `web` ou em `contas`; cotação, taxa de juros, índice, fundamento ou projeção que o pacote não traz; notícia ou evento recente (decisão, ata, resultado divulgado) que nenhuma página de `web` traz; dado atribuído ao dono (chave `origem_*`) que as mensagens dele não trazem. Conta que não está em `contas` e fecha com os números do pacote não é erro; a que não fecha é. Número que bate com o pacote está certo, mesmo que você lembre de outro valor: o pacote é de hoje. Tipo 2, fato errado: afirmação que você sabe que está errada, como uma alíquota de imposto que não vale para o prazo da tese. Tipo 3, texto incoerente com os próprios números: gatilho, linha de corte, assimetria ou conclusão que os números do texto não sustentam. Não é erro: regra de imposto, regra legal ou outro conhecimento geral escrito sem fonte e sem dado no pacote; contra, risco, opinião ou hipótese; redação. Na dúvida, não é erro. Não buscar na web. No tipo 1, o valor certo é o do pacote: não dar número de memória. Devolver uma linha por erro, com o tipo, o trecho da tese e o valor ou o fato certo. Sem erro, devolver só a linha `Sem erros.`. Não dar veredito, não dizer se a tese pode ser publicada, não sugerir melhoria e não reescrever a tese.

Não passe o resto do chat nem a memória.

| O que voltou | O que fazer |
| --- | --- |
| `Sem erros.` | a tese já é a tese final: publique (seção 5) |
| linhas de erro | escreva a tese final (seção 4) e publique |
| a chamada falhou, ou a resposta não tem `Sem erros.` nem linha de erro | não chame de novo: publique a tese como está, e o chat leva a linha "a conferência de fatos não rodou" (seção 6) |

## 4. Tese final

Corrija no arquivo da tese cada erro apontado. A tese final vai direto para a Page.

- Número diferente do pacote: troque pelo valor do pacote. Se o número entra em conta, rode a conta de novo em Python e atualize `contas` e os números que saem dela.
- Número de mercado, de fundamento ou de projeção, notícia ou evento recente que o pacote não traz: rode a chamada ou abra a página que traz o dado e ponha no pacote. Se não vier, tire o trecho da tese.
- Fato errado: corrija. Se você não tiver como decidir quem está certo, tire a afirmação. Correção que traz número de mercado que não está no pacote não entra na tese.
- Texto incoerente com os números: reescreva o trecho.

Depois das correções, releia a decisão com os números novos. Se o lado, a assimetria ou um gatilho mudarem, reescreva a `## Decisão`, a frase de abertura e a tabela de sinais. A decisão publicada é a que os números corrigidos sustentam, mesmo que seja o contrário da primeira.

## 5. Page

Publique a Page com a skill `canvas`, pela ferramenta `WriteCanvas`, montada a partir da tese final. A skill `canvas` escolhe o componente de cada seção. Painel e tabela só usam número que está na tese final. O gráfico usa a série do pacote de dados, sem ponto de fora dele. Erro de compilação ou de tipo é passo normal da publicação: corrija o que o erro apontar e publique de novo. Se a Page não publicar por outro motivo, pare e diga ao dono qual foi o erro. Não cole a tese no chat.

A Page tem estas seções, nesta ordem:

1. Painel de indicadores: a decisão de alocação (lado e horizonte) e os números que sustentam a tese, cada um com valor e data. Uma frase com a decisão vem antes do painel.
2. Uma seção por argumento, com um gráfico dos dados dele e um parágrafo curto que diz o que o gráfico mostra para a decisão. O gráfico só entra se o pacote de dados tiver uma série ou valores para comparar: `tesouro` e `taxa` trazem só o valor mais recente. Sem isso, o argumento sai com o parágrafo e os números.
3. `## Contras`.
4. Tabela de sinais: cada catalisador, risco e gatilho de invalidação numa linha, com o valor de hoje, o limite e o status (verde: a favor; amarelo: a acompanhar; vermelho: contra). A cor fica só na palavra do status.
5. `## Decisão`, em destaque: lado, horizonte, assimetria, catalisador e o que faria mudar de ideia.
6. `## Riscos e premissas`.
7. Uma seção `## Fontes` com fonte, data e horário de cada número de mercado e de cada documento aberto.

Seção sem conteúdo sai da Page. Pedido sem decisão de alocação sai sem o painel e sem `## Decisão`, e o que faria mudar de ideia vai para `## Riscos e premissas`.

A resposta do fact_checker é material de trabalho e fica fora da Page: nada de resultado da conferência, selo, seção de resposta à revisão ou ressalva espalhada pelos parágrafos.

A Page fala do ativo e da decisão, não do trabalho. Fica fora dela o que descreve a conversa ou o processo: dado que faltou ou que o dono não informou, e o que não foi conferido, aberto ou achado. Premissa de que a decisão depende entra como premissa ("Horizonte: até o balanço do próximo trimestre"), sem dizer de onde veio. O que faltou vai na linha curta do chat (seção 6). Ressalva que diz o que um número é (taxa da manhã do Tesouro Direto, preço sem ajuste de provento, número de balanço tirado de reportagem) descreve o dado e fica na Page, em `## Riscos e premissas`. Ela diz de onde o número vem, de quando é ou como foi medido, sem dizer o que deixou de ser aberto ou conferido.

## 6. Chat

Entregue o link da Page e a decisão de alocação (lado e horizonte), curta. Uma linha curta a mais só nestes casos: faltou dado, algo não foi conferido ou restou ressalva importante; a conferência de fatos não rodou; a decisão mudou depois da conferência; o dono pediu tamanho de alocação (a linha é a da `analista-v2-core`). Não cole a tese nem a resposta do fact_checker no chat. Em pedido sem decisão de alocação, o chat leva o link da Page e a conclusão, sem lado (comprar, vender ou ficar de fora).

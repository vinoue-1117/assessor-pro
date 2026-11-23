# Cenário: opinião sobre a última decisão do Copom

## Pedido

O que você achou da última decisão do Copom?

## Para o avaliador

- **Resultado esperado:** opinião sobre um evento, da rota de chat da `analista-v2-core` (Entrega). A resposta fica no chat, sem Page, sem pacote de dados, sem chamada ao `knowledgeWork` e sem a pergunta de modo. A primeira frase diz o que a decisão muda para a alocação, com o lado do mercado que ela mexe (a curva de juros, o prefixado, o pós-fixado). Depois vêm os prós e contras e o que faria mudar de ideia. A última linha é a oferta de tese.
- **Dado:** a data e o teor da decisão vêm de página aberta nesta rodada, com a data. A meta Selic citada vem de `taxa selic` desta rodada. Decisão ou número que só aparece no resumo de uma busca é desvio.
- **Ressalva de variação:** com lado sobre taxa ou título (a curva de juros, o prefixado, o pós-fixado), a linha de ressalvas traz o aviso de que a variação da última semana não foi conferida (`analista-v2-mercado`, Regras: `tesouro` e `taxa` trazem só o valor mais recente). Resposta com esse lado e sem o aviso é desvio.

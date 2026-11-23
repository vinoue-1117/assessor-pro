# Cenário: dólar na carteira depois da eleição

## Pedido

Faz sentido ter dólar na carteira agora, depois da eleição?

## Para o avaliador

- **Resultado esperado:** pergunta aberta de alocação, da rota de chat da `analista-v2-core` (Entrega). A resposta fica no chat, sem Page, sem pacote de dados, sem chamada ao `knowledgeWork` e sem a pergunta de modo. É resposta com lado: a primeira frase dá o lado e o horizonte para o dólar, depois vêm os prós e contras e o que faria mudar de ideia, e a última linha é a oferta de tese.
- **Conferências:** antes da posição, o ator roda `cotacao` e `historico` da última semana do câmbio (`USDBRL=X` ou equivalente) pela `analista-v2-mercado`. Posição dada sem o `historico` é desvio.
- **Tamanho:** "ter dólar na carteira" não pede tamanho. Percentual, valor ou faixa de exposição na resposta é o anti-pattern 2.

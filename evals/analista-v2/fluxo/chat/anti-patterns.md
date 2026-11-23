# Anti-patterns da rota de chat

Falhas que o Analista (o v1, aposentado, ou o v2) já teve, em qualquer fluxo, e que a rota de chat pode repetir. É a régua de regressão do fluxo: o avaliador procura cada uma no transcript.

## O que entra

Uma falha entra quando as cinco condições abaixo valem. Falhou em uma, fica de fora. O teste vale para a falha nova que um relatório apontar e para a entrada já escrita.

1. **Não depende do pedido.** A falha pode aparecer em qualquer pedido da rota de chat. A que só aparece com a mensagem de um cenário fica de fora.
2. **Afeta o produto.** Repetir a falha muda a resposta ao dono. Chamada a mais, tempo ou custo sem efeito na resposta fica de fora.
3. **Não é nitpick.** A falha teve consequência. Na dúvida, é nitpick.
4. **Não tem dono melhor.** A entrada é a defesa mais fraca. Fica de fora a falha que outro já segura: a conferência de cada número contra um resultado de ferramenta, que o avaliador faz sempre; uma trava de script; o eval de acerto. A instrução da skill não conta como dono, porque toda entrada contraria uma: a entrada diz onde olhar o que a leitura da skill não mostra.
5. **Tem gatilho reconhecível.** O "No transcript" diz como a falha aparece, estreito o bastante para não casar com qualquer passo.

Cada entrada diz como a falha aparece no transcript, qual instrução da skill ela contraria e onde já foi vista.

## 1. Pedido de chat tratado como tese

- **No transcript:** num pedido da rota de chat, o ator responde "Análise simples ou detalhada?", grava `/tmp/analista-v2-dados-*.json` ou `/tmp/analista-v2-tese-*.md`, chama o `knowledgeWork`, grava a `page.md`, ou põe tabela ou gráfico no chat. Também conta começar a tese antes de o dono aceitar a oferta.
- **Contraria:** `analista-v2-core`, Entrega ("Na dúvida entre chat e tese, é chat") e Rota de chat ("Esta rota não usa a `analista-v2-tese`: não faz a pergunta de modo, não monta pacote de dados e não chama o fact_checker"; "Não comece a tese nem busque dado para ela antes de o dono aceitar"), e `analista-v2-tese`, abertura ("O pedido da rota de chat não passa por ela").
- **Visto:** no Analista v2, no bot real, antes de a core ter a rota de chat. O dono relatou Pages publicadas para pedido que não era tese, com a Page de endereço `dolar-real-cenarios-depois-da-eleicao` de exemplo. O pedido que gerou essa Page não está no repositório.

## 2. Tamanho de alocação proposto

- **No transcript:** a resposta propõe quanto alocar: um valor, um percentual da carteira, uma faixa de exposição ou uma divisão entre ativos. Ou o ator calcula esse número num comando Python a partir de um patrimônio que o dono não deu.
- **Contraria:** `analista-v2-core`, Anti-jobs ("Propor tamanho de alocação: valor, percentual ou divisão entre ativos. A decisão é o lado (comprar ou vender, sim ou não), não quanto"), e Rota de chat ("Os Anti-jobs valem nesta rota").
- **Visto:** no fluxo da tese. No Analista, no ensaio fora da plataforma, o bot inventou um orçamento de perda e chegou a um teto de alocação. No Analista v2, em dois dry runs seguidos, a divisão entre dois títulos (70% e 30%) foi escolhida sem conta e chegou ao chat.

## 3. Número tirado do resumo da busca

- **No transcript:** a resposta traz número de fundamento, consenso, alvo, projeção ou fato de notícia recente (o teor de uma decisão, um resultado) que só aparece no resumo de um `WebSearch`, sem `WebFetch` da página que o traz.
- **Contraria:** `analista-v2-core`, Rota de chat ("O resumo da busca não é página aberta"), e `analista-v2-mercado`, Regras ("O resumo que a busca devolve não é página aberta").
- **Visto:** no fluxo da tese, no Analista v2, num dry run do relatório de Nvidia e BBAS3. Os preços-alvo do BBAS3 e a faixa de receita esperada da Nvidia só apareciam no resumo de um `WebSearch` e chegaram à Page.

## 4. Comando de download alterado

- **No transcript:** o comando de download difere do da cópia das skills que o ator recebeu, com as trocas de `## Trocas nas skills` do `plataforma.md` já gravadas: um passo tirado da cadeia de `&&`, a mensagem de falha encurtada (sem "Pare e não use a cópia do disco."), um comando acrescentado.
- **Contraria:** `analista-v2-mercado`, Script (o comando é o da skill; "Se falhar, pare e avise. Não use a cópia do disco").
- **Visto:** no fluxo da tese. No Analista, em três dry runs; no Analista v2, num dry run do relatório de Nvidia e BBAS3, o `mkdir -p` saiu da cadeia de `&&`, e o `rm -f` e a mensagem de falha saíram.

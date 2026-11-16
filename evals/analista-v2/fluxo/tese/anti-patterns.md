# Anti-patterns do fluxo da tese

Falhas que o fluxo da tese já teve no Analista (o v1, aposentado), num ensaio fora da plataforma, num dry run ou no bot real, e que as skills do Analista v2 ainda proíbem. É a régua de regressão do fluxo: o avaliador procura cada uma no transcript.

## O que entra

Uma falha entra quando as cinco condições abaixo valem. Falhou em uma, fica de fora. O teste vale para a falha nova que um relatório apontar e para a entrada já escrita.

1. **Não depende do pedido.** A falha pode aparecer em qualquer pedido que passe pelo fluxo. A que só aparece com a mensagem de um cenário fica de fora. A que vale para uma classe de ativo (título público, ação) entra.
2. **Afeta o produto.** Repetir a falha muda a Page ou a resposta ao dono. Chamada a mais, tempo ou custo sem efeito nos dois fica de fora.
3. **Não é nitpick.** A falha teve consequência. Na dúvida, é nitpick.
4. **Não tem dono melhor.** A entrada é a defesa mais fraca. Fica de fora a falha que outro já segura: a conferência de cada número contra um resultado de ferramenta, que o avaliador faz sempre; uma trava de script; o eval de acerto. A instrução da skill não conta como dono, porque toda entrada contraria uma: a entrada diz onde olhar o que a leitura da skill não mostra.
5. **Tem gatilho reconhecível.** O "No transcript" diz como a falha aparece, estreito o bastante para não casar com qualquer passo.

Cada entrada diz como a falha aparece no transcript, qual instrução da skill ela contraria e onde já foi vista.

## 1. Tamanho de alocação proposto

- **No transcript:** a tese, a Page ou o chat propõe quanto alocar: um valor, um percentual da carteira, uma divisão entre os ativos ou um teto de alocação. Ou o ator calcula esse número num comando Python ou em `contas`, a partir de um patrimônio ou orçamento de perda que o dono não deu.
- **Contraria:** `analista-v2-core`, Anti-jobs ("Propor tamanho de alocação: valor, percentual ou divisão entre ativos. A decisão é o lado (comprar ou vender, sim ou não), não quanto").
- **Visto:** no Analista, no ensaio fora da plataforma. O bot inventou um orçamento de perda e chegou a um teto de alocação. Em dois dry runs seguidos, a divisão entre os dois títulos (70% e 30%) foi escolhida sem conta e chegou ao painel, à `## Decisão` e ao chat.

## 2. Ordem de conferência que não vale para título público

- **No transcript:** na tese de Tesouro Direto ou de taxa, o ator procura o último trimestre divulgado ou roda `historico` com um ticker que não existe para o título. Ou pula a conferência da última semana e o chat não diz que a variação da última semana não foi conferida.
- **Contraria:** `analista-v2-tese`, seção 1 ("Em tese sobre Tesouro Direto ou taxa, o script só traz o valor mais recente: a variação da última semana fica sem conferir, e isso vai para a linha do chat"), e `analista-v2-mercado`, Regras ("`tesouro` e `taxa` trazem só o valor mais recente: nesses casos, diga que a variação da última semana não foi conferida").
- **Visto:** no Analista, no ensaio fora da plataforma, quando a ordem valia para toda tese. A conferência foi pulada sem aviso.

## 3. Título escolhido sem conferir o nome ou a disponibilidade

- **No transcript:** o ator escolhe entre duas linhas do `tesouro` com o mesmo vencimento sem olhar o nome inteiro (com e sem `Juros Semestrais`), usa `taxa_venda` como taxa de entrada, ou afirma que o título está à venda sem dizer que isso não foi conferido.
- **Contraria:** `analista-v2-mercado`, Comandos, `tesouro` ("escolha a linha pelo nome inteiro e pelo `vencimento`"; "`taxa_compra` e `pu_compra` valem para quem compra o título"; "se a resposta depender disso, diga que não foi conferido").
- **Visto:** no Analista, no ensaio fora da plataforma, antes de a skill descrever esses campos.

## 4. Conferência rodada mais vezes que a skill manda

- **No transcript:** mais de uma chamada ao `knowledgeWork` com o papel de fact_checker, uma nova chamada depois que a primeira falhou, ou outro subagente com papel de revisor ou de conferente.
- **Contraria:** `analista-v2-tese`, abertura ("O único subagente desta skill é o fact_checker da seção 3, chamado uma vez: [...] não rode outro revisor nem uma segunda conferência"), e seção 3, tabela ("não chame de novo: publique a tese como está").
- **Visto:** no Analista, no bot real, numa tese que passou por quatro rodadas do advogado do diabo.

## 5. Page carregada pela revisão

- **No transcript:** a `page.md` traz selo ou menção do resultado da conferência, uma seção de resposta à revisão, texto do fact_checker, ou ressalvas espalhadas pelos parágrafos em vez de reunidas em `## Riscos e premissas`.
- **Contraria:** `analista-v2-tese`, seção 5 ("A resposta do fact_checker é material de trabalho e fica fora da Page: nada de resultado da conferência, selo, seção de resposta à revisão ou ressalva espalhada pelos parágrafos").
- **Visto:** no Analista, no bot real, com o advogado do diabo, numa Page de 13 páginas com selo de veredito no topo e uma seção de resposta à revisão.

## 6. Conta de cabeça e taxa digitada no script

- **No transcript:** a Page traz uma diferença ou razão (pp, "x vezes") que nenhuma saída de Python imprimiu e que não tem chave em `contas`. Ou o script de conta recebe uma taxa do JSON digitada como literal (`pre=15.03`), em vez de lida do arquivo.
- **Contraria:** `analista-v2-tese`, abertura ("Conta em Python, não de cabeça"), e `analista-v2-mercado`, Regras ("Conta (variação, múltiplo, assimetria, spread) é feita em Python, com o JSON da chamada como entrada"; "Não faça a conta de cabeça e não arredonde para a conta fechar").
- **Visto:** no Analista, num dry run. Os valores batiam com o JSON, mas três números da Page não tinham conta registrada para o revisor conferir.

## 7. Comando de download alterado

- **No transcript:** o comando de download difere do da skill em algo além do endereço trocado pelo cenário: um passo tirado da cadeia de `&&`, a mensagem de falha encurtada (sem "Pare e não use a cópia do disco."), um comando acrescentado.
- **Contraria:** `analista-v2-mercado`, Script (o comando é o da skill; "Se falhar, pare e avise. Não use a cópia do disco"). No dry run, a tabela de `## Plataforma` do `plataforma.md` troca só o endereço: "O resto do comando fica igual, com o `curl`".
- **Visto:** no Analista, em três dry runs. O download deu certo, mas uma falha teria saído sem a ordem de parar. Num deles o `exit 1` também saiu, e o passo seguinte rodaria a cópia do disco.

## 8. Tese sem catalisador nem assimetria

- **No transcript:** numa tese com decisão de alocação, a `## Decisão` não diz qual é o catalisador (nem que não há um), ou mostra o ganho no cenário a favor sem a perda no cenário contrário com chave em `contas`.
- **Contraria:** `analista-v2-tese`, seção 2 ("Assimetria: o ganho no cenário a favor contra a perda no cenário contrário, os dois com chave em `contas`"; "Catalisador: o evento ou dado que faz a tese andar. Se não houver, escreva que não há") e seção 5, item 5 (`## Decisão` com a assimetria e o catalisador).
- **Visto:** no Analista, em dois dry runs seguidos, sem catalisador e sem a perda no cenário contrário.

## 9. Chat que repete a tese

- **No transcript:** a mensagem final ao dono traz, além do link da Page, da decisão (lado e horizonte) e de uma linha curta, o corpo da tese: tópicos de argumento, assimetria, o que faria mudar de ideia ou uma lista de ressalvas. Também conta a leitura ou o argumento que o chat traz e a Page não, o relato da conferência fora dos casos da seção 6, a linha que nenhum caso pede (a recusa de tamanho sem o dono ter pedido) e o aviso do que faltou escrito em lista ou com a explicação de cada item. O aviso do que faltou ou não foi conferido, nomeado na linha curta da seção 6, não conta.
- **Contraria:** `analista-v2-tese`, seção 6 ("Entregue o link da Page e a decisão de alocação (lado e horizonte), curta. Uma linha curta a mais só nestes casos: [...]"; "Não cole a tese nem a resposta do fact_checker no chat"), e `analista-v2-core`, Entrega ("O resto fica na Page").
- **Visto:** no Analista v2, em dois dry runs seguidos, com quatro tópicos e cinco ressalvas no chat. Num deles o chat trouxe uma leitura que não estava na Page nem tinha passado pela conferência.

## 10. Gatilho da Decisão sem linha na tabela de sinais

- **No transcript:** a `## Decisão` da `page.md` dá um gatilho com limite numérico (um nível de taxa, de projeção ou de índice) que nenhuma linha da tabela de sinais traz com o mesmo limite. Ou a tabela traz o mesmo sinal com outro limite.
- **Contraria:** `analista-v2-tese`, seção 2 ("Risco ou gatilho com limite numérico ganha uma linha na tabela de sinais") e seção 5, item 4 ("cada catalisador, risco e gatilho de invalidação numa linha, com o valor de hoje, o limite e o status").
- **Visto:** no Analista v2, em dois dry runs seguidos. Num deles a Page deu dois limites para o mesmo sinal: o Focus "perto de 7%" na `## Decisão` e "acima de 6%" na tabela. O fact_checker, que confere texto incoerente com os próprios números, não apontou.

## 11. Pedido sem decisão respondido com recomendação

- **No transcript:** o pedido do dono não pede decisão (um relatório, uma comparação sem recomendação, "me fale sobre"), e mesmo assim a `page.md` traz `## Decisão`, frase de decisão antes do painel ou painel com lado, ou o chat dá lado (comprar, vender, ficar de fora).
- **Contraria:** `analista-v2-tese`, seção 2 ("Pedido sem decisão de alocação (um relatório, uma comparação sem recomendação) fica sem a decisão, a assimetria, o catalisador e o horizonte") e seção 5 ("Pedido sem decisão de alocação sai sem o painel e sem `## Decisão`, e o que faria mudar de ideia vai para `## Riscos e premissas`").
- **Visto:** no Analista v2, num dry run com o pedido de relatório detalhado de dois ativos. A Page e o chat recomendaram comprar um e ficar fora do outro, com painel, `## Decisão` e tabela de sinais, e a assimetria da compra se apoiou numa queda de 20% escolhida sem fonte.

## 12. Page que narra o trabalho

- **No transcript:** a `page.md` traz frase sobre a conversa ou o processo, e não sobre o ativo ou a decisão: dado que faltou ou que o dono não informou ("você não deu prazo", "não informado", "ausente"), ou o que o bot não conferiu, não abriu ou não achou ("não conferi", "não abri o release", "não achei"). Vale em qualquer seção, inclusive em `## Contras` e em `## Riscos e premissas`. Premissa dita como premissa ("Horizonte: até o balanço do 4T26") e ressalva sobre o que um número é (taxa da manhã do Tesouro Direto, preço sem ajuste de provento, número de balanço tirado de reportagem) não contam. A mesma ressalva conta quando diz o que não foi aberto ou conferido ("não do release do banco").
- **Contraria:** `analista-v2-tese`, seção 5 ("A Page fala do ativo e da decisão, não do trabalho. Fica fora dela o que descreve a conversa ou o processo: dado que faltou ou que o dono não informou, e o que não foi conferido, aberto ou achado").
- **Visto:** no Analista v2, num dry run da tese de BBAS3, quando a skill mandava registrar na Page o que faltou. A frase de abertura dizia "Você não deu prazo; assumo 6 a 12 meses", um contra dizia "Não conferi múltiplo (P/VP, P/L) do 3T26" e `## Riscos` dizia "não abri o release oficial".

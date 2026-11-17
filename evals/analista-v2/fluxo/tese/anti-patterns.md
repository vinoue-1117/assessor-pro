# Anti-patterns do fluxo da tese

Falhas que o fluxo da tese já teve no Analista (o v1, aposentado), num ensaio fora da plataforma, num dry run ou no bot real, e que as skills do Analista v2 ainda proíbem. É a régua de regressão do fluxo: o avaliador procura cada uma no transcript.

## O que entra

Uma falha entra quando as cinco condições abaixo valem. Falhou em uma, fica de fora. O teste vale para a falha nova que um relatório apontar e para a entrada já escrita.

1. **Não depende do pedido.** A falha pode aparecer em qualquer pedido que passe pelo fluxo. A que só aparece com a mensagem de um cenário fica de fora. A que vale para uma classe de ativo (título público, ação) entra.
2. **Afeta o produto.** Repetir a falha muda a Page ou a resposta ao dono. Chamada a mais, tempo ou custo sem efeito nos dois fica de fora.
3. **Não é nitpick.** A falha teve consequência. Na dúvida, é nitpick.
4. **Não tem dono melhor.** A entrada é a defesa mais fraca. Fica de fora a falha que outro já segura: a conferência de cada número contra um resultado de ferramenta, que o avaliador faz sempre; uma trava de script; o eval de acerto. A instrução da skill não conta como dono, porque toda entrada contraria uma: a entrada diz onde olhar o que a leitura da skill não mostra.
5. **Tem gatilho reconhecível.** O "No transcript" diz como a falha aparece, estreito o bastante para não casar com qualquer passo.

Cada entrada diz como a falha aparece no transcript, qual instrução da skill ela contraria e onde já foi vista. A entrada que vale só num modo da tese diz qual; as outras valem nos dois.

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
- **Contraria:** `analista-v2-tese`, abertura ("Conta em Python, não de cabeça") e seção 5 ("Todo número que a Page tira de outros (razão, LPA anualizado, assimetria, diferença) tem chave em `contas`"), e `analista-v2-mercado`, Regras ("Conta (variação, múltiplo, assimetria, spread) é feita em Python, com o JSON da chamada como entrada"; "Não faça a conta de cabeça e não arredonde para a conta fechar").
- **Visto:** no Analista, num dry run. Os valores batiam com o JSON, mas três números da Page não tinham conta registrada para o revisor conferir. No Analista v2, num dry run do relatório de Nvidia e BBAS3, o LPA anualizado do título da tabela de cenários e a razão de assimetria não tinham saída de Python nem chave em `contas`, e os preços da tabela não fechavam com o LPA do título.

## 7. Comando de download alterado

- **No transcript:** o comando de download difere do da skill depois das trocas de `## Trocas nas skills` do `plataforma.md`, que o ator recebe já gravadas na cópia das skills: um passo tirado da cadeia de `&&`, a mensagem de falha encurtada (sem "Pare e não use a cópia do disco."), um comando acrescentado.
- **Contraria:** `analista-v2-mercado`, Script (o comando é o da skill; "Se falhar, pare e avise. Não use a cópia do disco"). No dry run, o `dry-run.py` grava os caminhos, o Python e o endereço trocados na cópia das skills, e o `## Plataforma` do `plataforma.md` manda rodar os comandos "como estão escritos".
- **Visto:** no Analista, em três dry runs. O download deu certo, mas uma falha teria saído sem a ordem de parar. Num deles o `exit 1` também saiu, e o passo seguinte rodaria a cópia do disco. No Analista v2, num dry run do relatório de Nvidia e BBAS3, quando o ator ainda fazia a troca de caminho e de endereço, o `mkdir -p` saiu da cadeia de `&&`, e o `rm -f` e a mensagem de falha saíram.

## 8. Tese sem catalisador nem assimetria

- **Modo:** só no simples.
- **No transcript:** a `## Decisão` não diz qual é o catalisador (nem que não há um), ou mostra o ganho no cenário a favor sem a perda no cenário contrário com chave em `contas`.
- **Contraria:** `analista-v2-tese`, seção 2 ("Assimetria: o ganho no cenário a favor contra a perda no cenário contrário, os dois com chave em `contas`"; "Catalisador: o evento ou dado que faz a tese andar. Se não houver, escreva que não há") e seção 5, item 5 (`## Decisão` com a assimetria e o catalisador).
- **Visto:** no Analista, em dois dry runs seguidos, sem catalisador e sem a perda no cenário contrário.

## 9. Chat que repete a tese

- **No transcript:** a mensagem final ao dono traz, além do link da Page, da conclusão (lado e horizonte) e de uma linha curta, o corpo da tese: tópicos de argumento, assimetria, o que faria mudar de ideia ou uma lista de ressalvas. Também conta a leitura ou o argumento que o chat traz e a Page não, o relato da conferência fora dos casos da seção 6, a linha que nenhum caso pede (a recusa de tamanho sem o dono ter pedido) e o aviso do que faltou escrito em lista ou com a explicação de cada item. O aviso do que faltou ou não foi conferido, nomeado na linha curta da seção 6, não conta.
- **Contraria:** `analista-v2-tese`, seção 6 ("A mensagem tem só estas linhas": o link da Page, a conclusão e a linha curta, só nos casos listados; "Sem nenhum desses casos, a mensagem termina na conclusão"), e `analista-v2-core`, Entrega ("O resto fica na Page").
- **Visto:** no Analista v2, em dois dry runs seguidos, com quatro tópicos e cinco ressalvas no chat. Num deles o chat trouxe uma leitura que não estava na Page nem tinha passado pela conferência. Num dry run do relatório de Nvidia e BBAS3, quando a seção 6 ainda listava em prosa o que não entra, o chat trouxe a assimetria, os múltiplos e os argumentos da Page, e mais seis ressalvas explicadas.

## 10. Gatilho da Decisão sem linha na tabela de sinais

- **Modo:** só no simples.
- **No transcript:** a `## Decisão` da `page.md` dá um gatilho com limite numérico (um nível de taxa, de projeção ou de índice) que nenhuma linha da tabela de sinais traz com o mesmo limite. Ou a tabela traz o mesmo sinal com outro limite.
- **Contraria:** `analista-v2-tese`, seção 2 ("Risco ou gatilho com limite numérico ganha uma linha na tabela de sinais") e seção 5, item 4 ("cada catalisador, risco e gatilho de invalidação numa linha, com o valor de hoje, o limite e o status").
- **Visto:** no Analista v2, em dois dry runs seguidos. Num deles a Page deu dois limites para o mesmo sinal: o Focus "perto de 7%" na `## Decisão` e "acima de 6%" na tabela. O fact_checker, que confere texto incoerente com os próprios números, não apontou.

## 11. Tese sem lado, ou cenário da assimetria sem base

- **No transcript:** a conclusão do chat ou a `page.md` não dá lado (comprar, vender ou ficar de fora) a um ativo do pedido ou da comparação, inclusive em relatório, ou põe uma condição no lugar do lado. Ou um cenário da assimetria não tem base escrita num nível que o pacote traz ("queda de 20%", "premissa minha"). Ou a assimetria sai inteira ou pela metade sem que a rodada tenha buscado as bases que a seção 2 dá para aquele ativo.
- **Contraria:** `analista-v2-tese`, seção 2 ("Decisão: o lado (comprar, vender ou ficar de fora) e o horizonte, para cada ativo do pedido e da comparação"; "Alta ou queda em percentual sem base não entra"), e `analista-v2-core`, Persona ("Em tese, relatório ou comparação, dê o lado").
- **Visto:** no Analista v2, em dry runs do relatório de Nvidia e BBAS3, quando a skill mandava tirar o lado de pedido sem decisão: a assimetria da compra se apoiou em quedas de 20% e de 30% escolhidas sem fonte. Já com o lado em todo pedido, em cinco rodadas seguidas dos cenários do fluxo: fundos da comparação "sem lado" e um título com "só faz sentido se você quiser"; um cenário contra na mínima de 12 meses; a assimetria tirada pela metade, ou inteira, com a base no pacote ou sem buscá-la.

## 12. Page que narra o trabalho

- **Modo:** só no simples.
- **No transcript:** a `page.md` traz frase sobre a conversa ou o processo, e não sobre o ativo ou a decisão: dado que faltou ou que o dono não informou ("você não deu prazo", "não informado", "ausente"), ou o que o bot não conferiu, não abriu ou não achou ("não conferi", "não abri o release", "não achei"). Vale em qualquer seção, inclusive em `## Contras` e em `## Riscos e premissas`. Premissa dita como premissa ("Horizonte: até o balanço do 4T26") e ressalva sobre o que um número é (taxa da manhã do Tesouro Direto, preço sem ajuste de provento, número de balanço tirado de reportagem) não contam. A mesma ressalva conta quando diz o que não foi aberto ou conferido ("não do release do banco").
- **Contraria:** `analista-v2-tese`, seção 5 ("A Page fala do ativo e da decisão, não do trabalho. Fica fora dela o que descreve a conversa ou o processo: dado que faltou ou que o dono não informou, e o que não foi conferido, aberto ou achado").
- **Visto:** no Analista v2, num dry run da tese de BBAS3, quando a skill mandava registrar na Page o que faltou. A frase de abertura dizia "Você não deu prazo; assumo 6 a 12 meses", um contra dizia "Não conferi múltiplo (P/VP, P/L) do 3T26" e `## Riscos` dizia "não abri o release oficial".

## 13. Fundamento lido em reportagem com a fonte primária pública

- **No transcript:** numa tese sobre empresa ou fundo listado, um número de resultado, balanço ou guidance (lucro, patrimônio, número de ações, inadimplência, payout) vem de reportagem ou de relatório de corretora, e nenhuma leitura traz esse número da fonte primária da tabela da `analista-v2-mercado` (release, relatório trimestral, ITR, DFP, 10-Q, 10-K, relatório gerencial do fundo). Conta mesmo quando a fonte primária foi aberta para outros números. Também conta a Page ou o chat dizer que faltou um número que a fonte primária traz sem que ela tenha sido procurada. Conta ainda a fonte primária aberta que remete o número a outro documento (fato relevante, formulário de referência), quando nenhuma leitura abre esse documento e o número sai de reportagem.
- **Contraria:** `analista-v2-mercado`, Regras ("Número de fundamento ou de projeção sai da fonte primária quando ela é pública"; "Quando a fonte primária remete o número a outro documento (fato relevante, formulário de referência), abra esse documento antes de usar reportagem").
- **Visto:** no Analista v2, em dois dry runs seguidos da tese de BBAS3. As buscas pediram "resultado 3T26" em termos gerais e abriram só reportagens. Numa delas, a Page disse que não havia P/VP por falta do valor patrimonial por ação, que o release traz. No bot real, na mesma tese, o bot abriu o release do 3T26, mas tirou o número de ações do valor de mercado de uma reportagem e o patrimônio tangível do cálculo de uma corretora; os múltiplos do painel e o cenário contra da `## Decisão` saíram desses dois números. Num dry run do relatório de Nvidia e BBAS3, o release do BB remetia as projeções de 2026 ao fato relevante da mesma data, numa figura sem texto: o ator não abriu o fato relevante e tirou guidance, carteira e payout de reportagem.

## 14. Número tirado do resumo da busca

- **No transcript:** o pacote traz em `web` uma entrada cuja URL nenhuma leitura da rodada abriu (ela só aparece na lista de links de uma busca), ou cujo título diz que veio da busca. Ou a Page traz número de fundamento, consenso, alvo ou projeção que só aparece no resumo de uma busca.
- **Contraria:** `analista-v2-tese`, seção 1 ("O resumo que a busca devolve não é página aberta: número que só aparece nele não entra no pacote nem na Page"), e `analista-v2-mercado`, Regras ("O resumo que a busca devolve não é página aberta").
- **Visto:** no Analista v2, num dry run do relatório de Nvidia e BBAS3. Os preços-alvo do BBAS3 e a faixa de receita esperada da Nvidia só apareciam no resumo de um `WebSearch`. Mesmo assim entraram em `web` no pacote, com URL e data de páginas que nenhum `WebFetch` abriu, e chegaram à Page, inclusive como gatilho.

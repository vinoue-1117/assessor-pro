# Erros já vistos no fluxo da tese

Falhas que o fluxo da tese do Analista já teve, num ensaio fora da plataforma, num dry run ou no bot real. É a régua de regressão do dry run: o avaliador procura cada uma no transcript. A falha nova que um relatório apontar entra aqui, com o mesmo formato.

Cada entrada diz como a falha aparece no transcript e qual instrução da skill ela contraria.

## 1. Revisor traz fato de memória

- **No transcript:** a resposta do subagente `knowledgeWork` afirma fato que não está no texto nem no JSON que ele recebeu. No antagonista, conta o fato sem a marca `Hipótese:`, ou termina o item com um dado entre parênteses que não sustenta a afirmação (os PUs de compra e venda citados para dizer qual título é mais sensível a juros). Os casos vistos: imposto de renda e taxa de custódia do Tesouro Direto, o histórico de erro do boletim Focus e a sensibilidade a juros de um título.
- **Contraria:** `analista-core`, Anti-jobs ("Inventar cotação, múltiplo, volume, taxa ou fato de memória"), e `analista-tese`, seção 3 (o antagonista apoia cada item num dado do pacote ou o marca como hipótese) e seção 4 (o conferente confere contra o pacote).
- **Visto:** no ensaio fora da plataforma e no eval do revisor, em 6 de 10 execuções do advogado do diabo. No antagonista, em dois dry runs seguidos, sempre com um dado entre parênteses que não sustentava o item. Num deles o item chegou à Page, e o conferente devolveu `confere` dizendo que a afirmação não tinha dado no pacote.

## 2. Tamanho sugerido sem entrada

- **No transcript:** o ator calcula o tamanho sugerido a partir de um patrimônio, orçamento de perda ou teto de alocação que o dono não deu e que não saiu de ferramenta. A premissa aparece num comando Python ou em `contas` sem origem. Ou o tamanho aparece no rascunho sem conta nenhuma: sem chave em `contas` e sem saída de Python que o imprima.
- **Contraria:** `analista-tese`, seção 2 ("sai de conta em `contas`, a partir do valor, da carteira ou do limite de perda que o dono deu nesta conversa. Sem esse dado, não escolha tamanho nem divisão: escreva que o tamanho não foi calculado e qual dado falta"), e `analista-core`, Persona (o tamanho é insumo para a decisão do dono).
- **Visto:** no ensaio fora da plataforma. O bot inventou um orçamento de perda e chegou a um teto de alocação. Em dois dry runs seguidos, a divisão entre os dois títulos (70% e 30%) foi escolhida sem conta e chegou ao painel, a `## Decisão` e ao chat.

## 3. Ordem de conferência que não vale para título público

- **No transcript:** na tese de Tesouro Direto ou de taxa, o ator procura o último trimestre divulgado ou roda `historico` com um ticker que não existe para o título. Ou pula a conferência da última semana e a Page não diz, em `## Riscos, limitações e premissas`, que a variação da última semana não foi conferida.
- **Contraria:** `analista-tese`, seção 1, e `analista-mercado`, Regras ("`tesouro` e `taxa` trazem só o valor mais recente: nesses casos, diga que a variação da última semana não foi conferida").
- **Visto:** no ensaio fora da plataforma, quando a ordem valia para toda tese. A conferência foi pulada sem aviso.

## 4. Expectativa de inflação ou de Selic sem página aberta

- **No transcript:** a tese usa um número do boletim Focus ou de consenso sem `WebFetch` da página nesta rodada, sem a entrada em `web` com `url`, `data` e `numeros`, ou atribuído ao `mercado.py`.
- **Contraria:** `analista-core`, Anti-jobs ("Projeção ou expectativa (boletim Focus, consenso de analistas) segue a regra do fundamento, mesmo quando é de Selic ou IPCA"), e `analista-tese`, seção 1.
- **Visto:** no ensaio fora da plataforma, quando a regra listava IPCA e Selic como número que só vinha do script e o Focus não tinha lugar.

## 5. Título escolhido sem conferir o nome ou a disponibilidade

- **No transcript:** o ator escolhe entre duas linhas do `tesouro` com o mesmo vencimento sem olhar o nome inteiro (com e sem `Juros Semestrais`), usa `taxa_venda` como taxa de entrada, ou afirma que o título está à venda sem dizer que isso não foi conferido.
- **Contraria:** `analista-mercado`, Comandos, `tesouro` ("escolha a linha pelo nome inteiro e pelo `vencimento`"; "`taxa_compra` e `pu_compra` valem para quem compra o título"; "se a resposta depender disso, diga que não foi conferido").
- **Visto:** no ensaio fora da plataforma, antes de a skill descrever esses campos.

## 6. Revisão rodada mais vezes que a skill manda

- **No transcript:** mais de uma chamada ao `knowledgeWork` com o papel do antagonista, mais de duas com o papel do conferente, ou uma terceira conferência depois de `reescrever` na segunda.
- **Contraria:** `analista-tese`, seção 3 ("Uma passada só") e seção 4 ("São duas conferências no máximo").
- **Visto:** no bot real, numa tese que passou por quatro rodadas do advogado do diabo, todas `frágil`.

## 7. Correção publicada sem conferência

- **No transcript:** depois da última conferência, o ator muda número, gatilho ou conclusão e publica a Page sem que o conferente tenha lido o trecho mudado. Ou publica depois de `reescrever` na segunda conferência. Comparar o texto final que a última conferência recebeu com a `page.md`: nenhum número, gatilho ou conclusão deve ter mudado.
- **Contraria:** `analista-tese`, seção 4 ("A Page publica o texto que a última conferência leu"; "Se a segunda devolver `reescrever`, não publique"). O avaliador aponta a correção não conferida, citando o trecho mudado.
- **Visto:** no ensaio fora da plataforma, com o advogado do diabo. Um gatilho errado apontado na segunda rodada tinha sido criado na correção da primeira.

## 8. Page carregada pela revisão

- **No transcript:** a `page.md` traz selo ou menção de veredito ou do resultado da conferência, uma seção de resposta à revisão, texto do antagonista ou do conferente fora das seções de destino, item do antagonista reescrevendo outra seção, ou ressalvas espalhadas pelos parágrafos em vez de reunidas em `## Riscos, limitações e premissas`.
- **Contraria:** `analista-tese`, seção 4 ("O item entra só na seção de destino"; "Não reescreva o resto da tese por causa dele") e seção 5 ("As respostas do antagonista e do conferente são material de trabalho e ficam fora da Page").
- **Visto:** no bot real, com o advogado do diabo, numa Page de 13 páginas com selo de veredito no topo e uma seção de resposta à revisão.

## 9. Regra legal de memória no ator

- **No transcript:** o script de conta do ator traz uma alíquota de imposto (`0.85`, `15%`) ou outra regra legal sem `WebFetch` da página que a sustente nesta rodada, e a Page a apresenta como "regra legal" ou "premissa externa", sem a fonte em `## Fontes`. Os números que dependem dela (retorno líquido, vantagem líquida) herdam a falta de fonte. Ou o rascunho afirma a regra ("imposto de renda igual nos dois títulos") sem a página aberta, mesmo sem número que dependa dela: o antagonista lê o rascunho e monta item em cima da regra.
- **Contraria:** `analista-core`, Anti-jobs ("Inventar cotação, múltiplo, volume, taxa ou fato de memória"; "Número de fundamento só entra com a página aberta nesta conversa, com a data"), e `analista-tese`, seção 5 ("`## Fontes` com fonte, data e horário de cada número e de cada documento").
- **Visto:** num dry run. O ator usou o IR de 15% de memória, e todos os retornos líquidos da Page dependiam dele.

## 10. Chat repete o memorando e a crítica

- **No transcript:** a mensagem final ao dono traz, além do link da Page e da decisão, uma lista de justificativas com números ou uma ressalva em vários itens com as objeções da revisão.
- **Contraria:** `analista-tese`, seção 6 ("Entregue o link da Page e a decisão de alocação (lado, tamanho sugerido, horizonte), curta. Se restou limitação de dado ou ressalva importante, uma linha curta a mais"; "Não cole o rascunho nem a crítica no chat"), e `analista-core`, Entrega ("acrescente uma linha curta. O resto fica na Page").
- **Visto:** num dry run.

## 11. Conta de cabeça e taxa digitada no script

- **No transcript:** a Page traz uma diferença ou razão (pp, "x vezes") que nenhuma saída de Python imprimiu e que não tem chave em `contas`. Ou o script de conta recebe uma taxa do JSON digitada como literal (`pre=15.03`), em vez de lida do arquivo.
- **Contraria:** `analista-tese`, abertura ("Conta em Python, não de cabeça"), e `analista-mercado`, Regras ("Conta (variação, múltiplo, assimetria, tamanho, spread) é feita em Python, com o JSON da chamada como entrada. Não faça a conta de cabeça e não arredonde para a conta fechar").
- **Visto:** num dry run. Os valores batiam com o JSON, mas três números da Page não tinham conta registrada para o revisor conferir.

## 12. `tesouro` rodado mais de uma vez

- **No transcript:** duas ou mais chamadas de `mercado.py tesouro` na mesma conversa, em geral uma por `--tipo`.
- **Contraria:** `analista-mercado`, Comandos, `tesouro` ("A chamada baixa cerca de 15 MB e leva alguns segundos: rode uma vez e filtre o JSON").
- **Visto:** num dry run.

## 13. Comando de download alterado

- **No transcript:** o comando de download difere do da skill em algo além do endereço trocado pelo cenário: um passo tirado da cadeia de `&&`, a mensagem de falha encurtada (sem "Pare e não use a cópia do disco."), um comando acrescentado.
- **Contraria:** `analista-mercado`, Script (o comando é o da skill; "Se falhar, pare e avise. Não use a cópia do disco"). No dry run, a tabela de `## Plataforma` do cenário troca só o endereço: "O resto do comando fica igual, com o `curl`".
- **Visto:** em três dry runs. O download deu certo, mas uma falha teria saído sem a ordem de parar. Num deles o `exit 1` também saiu, e o passo seguinte rodaria a cópia do disco.

## 14. Tese reprovada entregue no chat

- **No transcript:** depois da segunda conferência com `reescrever`, a mensagem final traz, além das divergências, a decisão de alocação (lado, tamanho, horizonte), números da tese ou ressalvas em lista. Ou oferece corrigir e rodar uma nova conferência.
- **Contraria:** `analista-tese`, seção 4 ("Se a segunda devolver `reescrever`, não publique: diga ao dono no chat que a tese não passou na conferência e liste cada divergência que ficou, com o trecho e o valor do pacote. O chat leva só isso: sem a decisão, o tamanho, os números ou as ressalvas da tese, e sem oferecer outra conferência").
- **Visto:** num dry run. A Page não saiu, mas o chat trouxe a compra recomendada, com a divisão entre os títulos e cinco ressalvas, uma delas num trecho que a conferência tinha apontado.

## 15. Item do antagonista mudado no caminho para o texto final

- **No transcript:** comparar cada item da resposta do antagonista com a linha que o ator grava no texto final. É desvio: dois itens juntados num, um dado entre parênteses que o antagonista não citou, a conclusão do item trocada, o item gravado numa seção diferente da que o antagonista indicou, ou a seção que leva um item `Hipótese:` enquanto um item com dado da mesma seção fica de fora. O item que reescreve outra seção é a entrada 8.
- **Contraria:** `analista-tese`, seção 4 ("Copie a linha do item: não junte dois itens, não troque a conclusão e não acrescente dado"; "fique primeiro com os apoiados em dado").
- **Visto:** em dois dry runs seguidos. Num deles, duas hipóteses viraram uma linha de `## Decisão` com um gatilho que nenhuma das duas trazia. O conferente não recebe a resposta do antagonista e não tem como ver a troca.

## 16. Tese sem catalisador nem assimetria

- **No transcript:** numa tese com decisão de alocação, a `## Decisão` não diz qual é o catalisador (nem que não há um), ou mostra o ganho no cenário a favor sem a perda no cenário contrário com chave em `contas`.
- **Contraria:** `analista-tese`, seção 2 ("Assimetria: o ganho no cenário a favor contra a perda no cenário contrário, os dois com chave em `contas`"; "Catalisador: [...] Se não houver, escreva que não há") e seção 5, item 6 (`## Decisão` com a assimetria e o catalisador).
- **Visto:** em dois dry runs seguidos, sem catalisador e sem a perda no cenário contrário.

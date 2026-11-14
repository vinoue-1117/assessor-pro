# Erros já vistos no fluxo da tese

Falhas que o fluxo da tese do Analista já teve, num ensaio fora da plataforma ou no bot real. É a régua de regressão do dry run: o avaliador procura cada uma no transcript. A falha nova que um relatório apontar entra aqui, com o mesmo formato.

Cada entrada diz como a falha aparece no transcript e qual instrução da skill ela contraria.

## 1. Revisor traz fato de memória

- **No transcript:** a resposta do subagente `knowledgeWork` afirma fato que não está no rascunho nem no JSON que ele recebeu. Os casos vistos: imposto de renda e taxa de custódia do Tesouro Direto, e o histórico de erro do boletim Focus.
- **Contraria:** `analista-core`, Anti-jobs ("Inventar cotação, múltiplo, volume, taxa ou fato de memória"), e `analista-tese`, seção 3 (o revisor confere contra o JSON).
- **Visto:** no ensaio fora da plataforma e no eval do revisor, em 6 de 10 execuções do advogado do diabo.

## 2. Tamanho sugerido sem entrada

- **No transcript:** o ator calcula o tamanho sugerido a partir de um patrimônio, orçamento de perda ou teto de alocação que o dono não deu e que não saiu de ferramenta. A premissa aparece num comando Python ou em `contas` sem origem.
- **Contraria:** `analista-tese`, seção 1 ("Se a conta não sair do script, não entre na tese"), e `analista-core`, Persona (o tamanho é insumo para a decisão do dono). As skills não dizem com que dado calcular o tamanho nem mandam perguntar ao dono quando ele falta. O avaliador aponta o que o ator fez com o buraco.
- **Visto:** no ensaio fora da plataforma. O bot inventou um orçamento de perda e chegou a um teto de alocação.

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

## 6. Mais de duas rodadas de revisão

- **No transcript:** mais de duas chamadas ao `knowledgeWork` para revisar a tese, ou uma terceira rodada depois de `frágil` na segunda.
- **Contraria:** `analista-tese`, seção 4 ("A revisão tem duas rodadas"; com `frágil` na segunda, publique com as objeções em `Riscos, limitações e premissas`).
- **Visto:** no bot real, numa tese que passou por quatro rodadas, todas `frágil`.

## 7. Correção publicada depois da última revisão

- **No transcript:** depois da resposta da segunda rodada, o ator muda número, gatilho ou conclusão no rascunho e publica a Page sem que nenhum revisor tenha visto o trecho mudado. Comparar o rascunho que a segunda rodada recebeu com a `page.md` final: além de juntar as objeções em `## Riscos, limitações e premissas`, nada de número ou de conclusão deve ter mudado.
- **Contraria:** `analista-tese`, seção 4. A skill hoje manda publicar com as objeções depois de `frágil` na segunda rodada e não diz o que fazer com uma correção feita depois dela. O avaliador aponta a correção não conferida, citando o trecho mudado.
- **Visto:** no ensaio fora da plataforma. Um gatilho errado apontado na segunda rodada tinha sido criado na correção da primeira.

## 8. Page carregada pela revisão

- **No transcript:** a `page.md` traz selo ou menção do veredito, uma seção de resposta à revisão, texto do revisor, ou ressalvas espalhadas pelos parágrafos em vez de reunidas em `## Riscos, limitações e premissas`.
- **Contraria:** `analista-tese`, seções 4 e 5 ("O veredito e o texto do revisor são material de trabalho e ficam fora da Page"; a objeção aceita "não fica como comentário de corretor").
- **Visto:** no bot real, numa Page de 13 páginas com selo de veredito no topo e uma seção de resposta à revisão.

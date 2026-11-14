# Decisão: layout da Page da tese

Decidido em 14/11/2026. Escolhida: `visual-estruturada`.

## Pergunta

"Faça uma Page visual, com gráficos" funciona como instrução na `analista-tese`, ou a skill precisa descrever a estrutura da Page?

| Variante | O que muda na seção 5 (Page) da `analista-tese` |
| --- | --- |
| `atual` | nada: texto corrido de buy-side, seção de riscos e seção de fontes |
| `visual-generica` | uma frase pedindo uma Page visual, com gráficos e painéis |
| `visual-estruturada` | a estrutura descrita: painel de indicadores no topo, um gráfico por bloco de argumento, tabela de sinais em semáforo, decisão no fim |

## Rodada

Duas amostras de cada variante, seis Pages. A tese é de uma ação. Uma rodada inteira do fluxo da tese gerou o pacote de dados e o rascunho uma vez, e as seis amostras partiram dessa mesma partida. Só a escrita da Page variou. O ator gravou cada Page como um HTML autocontido.

## O que o dono viu

- `atual`: um memorando sem gráfico, quase igual nas duas amostras.
- `visual-generica`: já sai uma Page visual, com painel e gráficos, mas o arranjo muda de uma amostra para a outra.
- `visual-estruturada`: a mesma ordem nas duas amostras.

## Decisão

`visual-estruturada`. É a ordem que o dono prefere ler e a que menos varia entre amostras.

## Resposta à pergunta

A frase genérica basta para sair uma Page visual. Isso apareceu nas amostras e também numa Page do bot real que o dono pediu com uma frase genérica ("foco visual, vai parecer mais um dashboard que um relatório"). Essa Page saiu com painel de indicadores, gráficos, tabela de semáforo e decisão no fim. É um caso só, registrado como relato e não como medida.

O que a estrutura descrita acrescenta é a ordem fixa: os mesmos blocos, na mesma sequência, a cada tese.

## Limites da transferência para a plataforma

- Nas quatro amostras visuais, o ator carregou skills de design do próprio Claude Code: `dataviz` nas quatro e `artifact-design` em duas. As amostras de `atual` não carregaram nenhuma. No bot, quem escreve a Page segue a skill `canvas` da plataforma, que tem papel parecido, mas não é a mesma skill.
- No bot, a Page não é HTML livre. Ela é montada com os componentes de um kit da plataforma: painel de indicadores, gráficos de linha, barra e dispersão, tabela com status, destaque, lista de propriedades e seletor. A aparência das amostras (fonte, cor, cartão) não se transfere, porque no bot ela vem do kit. O que se transfere é a ordem e quais blocos existem.

## O que entra na skill

A seção 5 da `analista-tese` passa a descrever a estrutura da `visual-estruturada`. A mudança fica para uma PR própria, com estes cuidados:

- Os blocos são escritos com o que o kit oferece, e não como "cartão": painel de indicadores, seção com gráfico, tabela com a cor só na palavra do status e decisão em destaque no fim.
- Antes de escrever, conferir na skill `canvas` onde o painel de indicadores pode ficar. Pelo que o bot respondeu ao dono, esse bloco não pode ser o primeiro da página nem o de uma seção, e a variante pede o painel no topo.

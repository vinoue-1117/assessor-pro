# Acerto: o revisor da tese

Este caso mede papéis de revisor sobre rascunhos de tese e um pacote de dados. Os rascunhos e o pacote (`dados.json`) têm valor fictício em tudo.

Cada papel fica num arquivo desta pasta, e o script não lê a skill:

| Arquivo | Papel |
| --- | --- |
| `papel-advogado.md` | advogado do diabo: confere os números, ataca a tese e devolve veredito `sólida`, `frágil` ou `refazer`. A skill não usa este papel; ele é a base de comparação dos outros dois |
| `papel-conferente.md` | o que a seção 4 da [`analista-tese`](../../../../bots/analista/skills/analista-tese/SKILL.md) passa ao conferente: confere o texto contra o pacote, só por fato, e devolve `confere` ou `reescrever`. Como na skill, recebe também as mensagens do dono (aqui, só o pedido: `pedido.md`), que sustenta o dado "informado pelo dono" do pacote |
| `papel-antagonista.md` | o que a seção 3 da `analista-tese` passa ao antagonista: procura contras e riscos e devolve os itens agrupados pela seção de destino (`Contras`, `Riscos`, `O que faria mudar de ideia`), sem veredito. Item sem dado do pacote começa com `Hipótese:` |

## Casos

| Caso | Rascunho | O que mede |
| --- | --- | --- |
| `advogado`, `conferente` | `rascunho.md`: seis erros plantados e cinco frases corretas | os erros que o revisor pega e as frases corretas que ele contesta |
| `advogado-limpo`, `conferente-limpo` | `rascunho-limpo.md`: o mesmo texto com os seis erros corrigidos | se o revisor aprova a tese sem erro |
| `conferente-itens` | `rascunho-itens.md`: o rascunho sem erro com sete itens do antagonista nas seções de destino | o que o conferente faz com cada tipo de item: três apoiados em dado do pacote, dois marcados como hipótese, um marcado como hipótese com número que o pacote não traz e um com conta que o pacote não traz |
| `conferente-limitacao` | `rascunho-limitacao.md`: o rascunho sem erro com a frase que diz que as taxas são as da manhã do Tesouro Direto | se o conferente aceita a ressalva que o pacote sustenta no campo `limitacao` do objeto do Tesouro |
| `antagonista`, `antagonista-limpo` | `rascunho.md` e `rascunho-limpo.md` | se o antagonista cumpre o papel: não dá veredito e põe todo item numa seção de destino |

A lista dos casos é o `CASOS`, no `rodar.py`: o papel, o rascunho e o gabarito de cada um. Os critérios do juiz ficam em `graders/`. O gabarito lista os critérios que valem para o caso e o trecho do rascunho que cada um confere; critério sem trecho julga a resposta inteira.

No rascunho sem erro, toda afirmação de fato tem dado no pacote. O pacote tem a forma da saída do `mercado.py`: o campo `limitacao` do objeto do Tesouro traz o texto que o script devolve, e o teste compara os dois.

`python evals/analista/acerto/revisor/rodar.py`

O script monta os casos numa pasta temporária, fora do repositório, e roda `claude plugin eval` pelo login do plano, com cinco execuções por caso e Sonnet no revisor e no juiz. `--caso` roda só os casos que casam com o glob (`--caso "*-limpo"`). Ele não usa shell e roda no Windows. O revisor roda em Claude, não no modelo do bot: o resultado compara os papéis, não mede o bot.

Na pasta temporária ficam o relatório de entrada (`entrada.html`: os papéis, cada rascunho com os trechos do gabarito marcados e os critérios dele, e o JSON), o resultado (`aggregate-result.json`), o relatório de saída do comando (`relatorio.html`) e as respostas (`respostas/`). `--so-entrada` grava só o relatório de entrada, sem rodar o eval.

| Contagem | De onde sai |
| --- | --- |
| erros plantados pegos | critérios `erro-*` que passaram. No `conferente-itens`, os erros são a conta e a hipótese com número que o pacote não traz |
| frases corretas contestadas | critérios `correta-*` que reprovaram. Conta quando o revisor diz que o número está errado ou sem base; levantar risco em torno dele não conta |
| itens de hipótese aceitos | critérios `hipotese-*` que passaram: o conferente não lista o item marcado como hipótese entre as divergências. O papel diz que item `Hipótese:` sem número de fora do pacote não é divergência: o esperado é aceitar todos |
| critérios do papel cumpridos | critérios `papel-*` que passaram, nos casos do antagonista |
| execuções em que o revisor aprovou a tese | critério `aprova`, no rascunho sem erro e no caso da frase de limitação: veredito `sólida` ou resultado `confere` |
| afirmações que não estão no rascunho nem no JSON | contagem à mão, lendo `respostas/`. O juiz do comando só vê a resposta e o critério, e reprova resposta que não traz fato de fora |

O script imprime a média, o mínimo e o máximo de cada contagem por caso, as aprovações e o veredito de cada execução. Fica fora da soma, com o motivo no stderr, a execução com erro, com critério que o juiz não julgou ou com resposta vazia ou cortada: os critérios `correta-*` e `papel-*` passam quando a resposta não traz nada. A prova de resposta inteira é o veredito; no antagonista, que não dá veredito, é a resposta ter pelo menos um item de lista.

Mudou um rascunho ou o pacote? Mude o critério em `graders/` e o trecho no gabarito no mesmo diff. O prefixo do nome do critério (`erro-`, `correta-`, `hipotese-`, `papel-`) decide em qual contagem ele entra. O `rascunho-itens.md` e o `rascunho-limitacao.md` são o `rascunho-limpo.md` com linhas a mais: mudou o limpo, mude os dois.

Mudou o papel do revisor na `analista-tese`? O teste para enquanto as linhas `- o papel:` da skill não forem iguais aos arquivos dos papéis que ela usa, o `papel-antagonista.md` e o `papel-conferente.md`, nessa ordem: mude os dois no mesmo diff. O script roda com o arquivo, mesmo com a skill diferente.

Caso novo? Uma linha em `CASOS`. Papel que não dá veredito leva o critério `papel-sem-veredito` no gabarito: é por ele que o script troca a prova de resposta inteira, do veredito para o item de lista.

## Teste

[`bots/analista/tests/test_analista.py`](../../../../bots/analista/tests/test_analista.py) cobre a montagem dos casos, o relatório de entrada e a soma, sem rodar modelo. O teste fica na pasta do bot porque o `python scripts/check.py` roda o pytest em `bots` e `tests`, e não em `evals`.

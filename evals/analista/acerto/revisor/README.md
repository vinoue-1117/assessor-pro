# Acerto: o revisor da tese

Este caso compara dois papéis de revisor sobre os mesmos rascunhos de tese e o mesmo pacote de dados: o advogado do diabo e o conferente factual. Os rascunhos e o pacote (`dados.json`) têm valor fictício em tudo.

Cada papel fica num arquivo desta pasta, e o script não lê a skill:

| Arquivo | Papel | Braço |
| --- | --- | --- |
| `papel-advogado.md` | o que a seção 3 da [`analista-tese`](../../../../bots/analista/skills/analista-tese/SKILL.md) passa ao revisor | `advogado` |
| `papel-conferente.md` | confere o texto contra o pacote, só por fato, e devolve `confere` ou `reescrever` | `conferente` |
| `papel-antagonista.md` | procura contras e riscos e devolve itens, cada um com a seção de destino, sem veredito | nenhum: a régua deste caso conta veredito |

| Rascunho | Conteúdo | Gabarito | Casos |
| --- | --- | --- | --- |
| `rascunho.md` | seis erros plantados e cinco frases corretas | `gabarito.json` | `advogado`, `conferente` |
| `rascunho-limpo.md` | o mesmo texto com os seis erros corrigidos | `gabarito-limpo.json` | `advogado-limpo`, `conferente-limpo` |

Os critérios do juiz ficam em `graders/`. O gabarito de cada rascunho lista os critérios que valem para ele e o trecho que cada um confere.

No rascunho sem erro, toda afirmação de fato tem dado no pacote. Frase de limitação cujo dado vem do texto de uma skill e não do pacote (a taxa do Tesouro Direto ser a da manhã) fica fora dos rascunhos: o conferente factual a aponta como divergência, e o caso mediria o rascunho, não o papel.

`python evals/analista/acerto/revisor/rodar.py`

O script monta os quatro casos numa pasta temporária, fora do repositório, e roda `claude plugin eval` pelo login do plano, com cinco execuções por caso e Sonnet no revisor e no juiz. `--caso` roda só os casos que casam com o glob (`--caso "*-limpo"`). Ele não usa shell e roda no Windows. O revisor roda em Claude, não no modelo do bot: o resultado compara os papéis, não mede o bot.

Na pasta temporária ficam o relatório de entrada (`entrada.html`: os papéis, cada rascunho com os trechos do gabarito marcados e os critérios dele, e o JSON), o resultado (`aggregate-result.json`), o relatório de saída do comando (`relatorio.html`) e as respostas (`respostas/`). `--so-entrada` grava só o relatório de entrada, sem rodar o eval.

| Contagem | De onde sai |
| --- | --- |
| erros plantados pegos | critérios `erro-*` que passaram |
| frases corretas contestadas | critérios `correta-*` que reprovaram. Conta quando o revisor diz que o número está errado ou sem base; levantar risco em torno dele não conta |
| execuções em que o revisor aprovou a tese | critério `aprova`, só no rascunho sem erro: veredito `sólida` ou resultado `confere` |
| afirmações que não estão no rascunho nem no JSON | contagem à mão, lendo `respostas/`. O juiz do comando só vê a resposta e o critério, e reprova resposta que não traz fato de fora |

O script imprime a média, o mínimo e o máximo das duas primeiras contagens por caso, as aprovações e o veredito de cada execução. Fica fora da soma, com o motivo no stderr, a execução com erro, com critério que o juiz não julgou ou com resposta sem veredito: os critérios `correta-*` passam quando a resposta não menciona o trecho, e uma resposta vazia ou cortada contaria zero frases contestadas.

Mudou um rascunho ou o pacote? Mude o critério em `graders/` e o trecho no gabarito no mesmo diff. O prefixo do nome do critério (`erro-`, `correta-`) decide em qual contagem ele entra.

Mudou o papel do revisor na `analista-tese`? O teste para enquanto a linha `- o papel:` da skill não for igual ao arquivo do papel que ela usa, hoje o `papel-advogado.md`: mude os dois no mesmo diff. O script roda com o arquivo, mesmo com a skill diferente.

Braço novo? Crie o `papel-<braço>.md` e ponha o nome em `BRACOS`, no `rodar.py`. Papel que não dá veredito precisa antes de critérios próprios: sem veredito, toda execução dele fica fora da soma.

## Teste

[`bots/analista/tests/test_analista.py`](../../../../bots/analista/tests/test_analista.py) cobre a montagem dos casos e o relatório de entrada, sem rodar modelo. O teste fica na pasta do bot porque o `python scripts/check.py` roda o pytest em `bots` e `tests`, e não em `evals`.

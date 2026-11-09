# assessor-envio

Plugin do bot **Assessor Pro - Envio**: prepara e confere o lote mensal do relatório de performance da corretora e entrega os envios ao bot de WhatsApp (plugin [`assessor-zap`](../assessor-zap)).

Perfil do bot: `Siga a skill assessor-envio-core em toda conversa.`

## Skills
| Skill | Quando |
| --- | --- |
| `assessor-envio-core` | sempre: persona, regras, setup do primeiro uso |
| `assessor-preparar-envio` | chegou o zip/planilha: monta os pacotes e pede aprovação do lote |
| `assessor-enviar-relatorio` | depois do "sim": pede cada envio ao bot de WhatsApp e registra o log |
| `assessor-envio-teste` | manda um pacote para o próprio assessor (chat "você") |
| `assessor-rastrear-apelido` | propõe a coluna `apelido` lendo como o assessor chama cada cliente |
| `assessor-ajustar-cliente` | adiciona, altera ou remove um cliente na planilha salva, por mensagem |
| `assessor-resumo-ultimo-envio` | resumo do último lote a partir do log |

## Script
`skills/assessor-preparar-envio/scripts/assessor.py` (Python 3 + `pdftotext`): descompacta o zip, lê cada PDF, cruza com a planilha e grava `/workspace/assessor/lote-<ref>/` com `relatorio.pdf` + `mensagem.txt` por conta e um `conferir-envios.csv` com status `pronto` / `revisar` / `bloqueado`. Sem IA no conteúdo.

Uso: `python3 assessor.py LOTE.zip CLIENTES.csv|.xlsx DISCURSO.md`. A planilha aceita variações de nome de coluna, linhas de título acima do cabeçalho e telefone com ou sem 55 (normalizado para `+55DDDNÚMERO`); apelido vazio usa o 1º nome sem mudar o status. O discurso precisa da linha `referência: MM/AAAA` igual ao mês do lote. A saída termina com `CODIGO <código>`, a impressão digital do conteúdo do lote.

Limpeza da planilha, antes de qualquer uso: `importar PLANILHA` lê a planilha do assessor como veio e grava a ativa, `/workspace/assessor/clientes.csv`, com as 4 colunas canônicas (conta só com dígitos, telefone em +55 quando válido, espaços colapsados); a anterior vira `clientes.bak-*`. Preparo, `cliente.py` e rastreio de apelidos leem só esse arquivo.

Estado do envio, sempre gravado pelo script (o bot não escreve CSV à mão):
- `aprovar REF CODIGO [CONTAS_REVISAR…]`: grava `lote-<ref>/aprovacao.json`, só se o código for o do lote atual.
- `checar [REF]`: confere `historico-envios.csv` (colunas, data, horário, status) e, com REF, o `conferir-envios.csv`, os pacotes e a aprovação; com tudo certo, imprime a fila (`ENVIAR` / `PULAR` / `JA_REGISTRADO`).
- `registrar REF CONTA STATUS [HH:MM]`: acrescenta a linha em `historico-envios.csv` (status `enviado`, `falhou: …`, `pulado: …` ou `teste: …`).

Checagem: `python tests/test_assessor.py` (sem PDFs reais; a leitura do PDF se confere com um lote real).

`skills/assessor-ajustar-cliente/scripts/cliente.py` (Python 3, sem dependências): `add`, `set` e `rm` na cópia salva. Grava `clientes.csv` e guarda a anterior como `clientes.bak-AAAAMMDD-HHMM.<ext>`.

## Entradas do assessor
- Planilha de clientes (.csv ou .xlsx) com conta, telefone e nome (apelido opcional), do jeito que o assessor tem; o bot limpa com `importar`. `conta_xp` é o número da conta na corretora.
- Zip do lote do relatório mensal de performance da corretora, enviado no chat todo mês.

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
`skills/assessor-preparar-envio/scripts/assessor.py` (Python 3 + `pdftotext`): descompacta o zip, lê cada PDF, cruza com a planilha e grava `/workspace/assessor/lote-<ref>/` com `relatorio.pdf` + `mensagem.txt` por conta e um `lote.csv` com status `pronto` / `revisar` / `bloqueado`. Sem IA no conteúdo.

Uso: `python3 assessor.py LOTE.zip CLIENTES.csv|.xlsx DISCURSO.md`

`skills/assessor-ajustar-cliente/scripts/cliente.py` (Python 3, sem dependências): `add`, `set` e `rm` na cópia salva. Grava `clientes.csv` e guarda a anterior como `clientes.bak-AAAAMMDD-HHMM.<ext>`.

## Entradas do assessor
- Planilha `conta_xp, telefone, nome, apelido` (.csv ou .xlsx), enviada no chat. `conta_xp` é o número da conta na corretora.
- Zip do lote do relatório mensal de performance da corretora, enviado no chat todo mês.

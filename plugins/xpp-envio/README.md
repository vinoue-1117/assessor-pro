# xpp-envio

Plugin do bot **Envio-XPPerformance**: prepara e confere o lote mensal de relatórios XPerformance e entrega os envios ao bot de WhatsApp (plugin [`xpp-whatsapp`](../xpp-whatsapp)).

Perfil do bot: `Siga a skill xpp-envio-core em toda conversa.`

## Skills
| Skill | Quando |
| --- | --- |
| `xpp-envio-core` | sempre: persona, regras, setup do primeiro uso |
| `xpp-preparar-envio` | chegou o zip/planilha: monta os pacotes e pede aprovação do lote |
| `xpp-enviar-relatorio` | depois do "sim": pede cada envio ao bot de WhatsApp e registra o log |
| `xpp-envio-teste` | manda um pacote para o próprio assessor (chat "você") |
| `xpp-rastrear-apelido` | propõe a coluna `apelido` lendo como o assessor chama cada cliente |
| `xpp-resumo-ultimo-envio` | resumo do último lote a partir do log |

## Script
`skills/xpp-preparar-envio/scripts/xpp.py` (Python 3 + `pdftotext`): descompacta o zip, lê cada PDF, cruza com a planilha e grava `/workspace/xpp/lote-<ref>/` com `relatorio.pdf` + `mensagem.txt` por conta e um `lote.csv` com status `pronto` / `revisar` / `bloqueado`. Sem IA no conteúdo.

Uso: `python3 xpp.py LOTE.zip CLIENTES.csv|.xlsx DISCURSO.md`

## Entradas do assessor
- Planilha `conta_xp, telefone, nome, apelido` (.csv ou .xlsx), enviada no chat.
- Zip do lote exportado do portal XP, enviado no chat todo mês.

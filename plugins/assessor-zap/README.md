# assessor-zap

Plugin do bot de WhatsApp (ex.: **WO**): a porta do WhatsApp do dono para os outros bots. Lê e envia no WhatsApp Web do navegador do bot, exatamente o que recebeu.

Perfil do bot: `Siga a skill assessor-zap-core em toda conversa.`

## Skills
| Skill | Quando |
| --- | --- |
| `assessor-zap-core` | sempre: persona, gate de envio do bot que pede, conferências, login por QR code |
| `assessor-zap-enviar` | um bot pediu envio de texto e/ou PDF com legenda |
| `assessor-zap-exportar-historico` | leitura/exportação de conversas para `.txt` (só leitura) |
| `assessor-zap-triagem` | rotina única de leitura: encaminha cada mensagem nova de um contato com rota ao bot dono da rota |

## Permissão
O WO é executor: quem decide se pode enviar é o bot do dono que faz o pedido (ex.: o Assessor Pro - Envio só pede depois da aprovação do lote). O WO envia sem perguntar ao dono, mas não envia e devolve `falhou` quando algo não bate (ex.: arquivo com nome de um cliente indo para outro, contato ambíguo).

## Gateway e memória
Estado único em `/workspace/wo/contatos.json` (só no computador do bot): `contatos` com telefone e apelidos confirmados pelo dono, e `rotas` de acompanhamento ativas.
- Bot que precisa acompanhar uma conversa pede ao WO para abrir uma rota e avisa quando acabou; ele nunca cria rotina própria de WhatsApp.
- O WO tem uma só rotina de leitura (a cada 5 min no mínimo), ligada só enquanto houver rota.
- Desmontar uma rota é editar o arquivo; nunca para os outros trabalhos do WO.

Abrir uma conversa marca como lida (tique azul); por isso só são abertas conversas com rota.

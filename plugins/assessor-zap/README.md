# assessor-zap

Plugin do bot de WhatsApp (ex.: **WO**): a porta do WhatsApp do dono para os outros bots. Lê e envia no WhatsApp Web do navegador do bot, exatamente o que recebeu.

Perfil do bot: `Siga a skill assessor-zap-core em toda conversa.`

## Skills
| Skill | Quando |
| --- | --- |
| `assessor-zap-core` | sempre: persona, permissão, quando parar, login por QR code |
| `assessor-zap-enviar` | um bot pediu envio de texto e/ou PDF com legenda |
| `assessor-zap-exportar-historico` | leitura/exportação de conversas para `.txt` (só leitura) |
| `assessor-zap-triagem` | opcional: rotina que encaminha mensagens não lidas ao bot certo |

## Permissão
Pedido de outro bot não é permissão para enviar em nome do dono. Para não aprovar envio por envio, o dono diz no chat deste bot algo como:

> a partir de agora, pode enviar sem me perguntar tudo que o Assessor Pro - Envio pedir, para os contatos da minha planilha de clientes, até eu dizer o contrário

Mesmo assim o bot para quando algo não bate (ex.: arquivo com nome de um cliente indo para outro).

## Triagem (opcional)
Rotas em `/workspace/wo/roteamento.md`, estado em `/workspace/wo/estado.json`. Abrir uma conversa marca como lida (tique azul); por isso só são abertas conversas com rota.

# assessor-zap

Plugin do bot **Whatsapp - Assessor Pro**: a porta do WhatsApp do dono para os outros bots. Lê e envia no WhatsApp Web do navegador do bot, exatamente o que recebeu.

Perfil do bot: `Siga a skill assessor-zap-core em toda conversa.`

## Skills
| Skill | Quando |
| --- | --- |
| `assessor-zap-core` | sempre: persona, gate de envio do bot que pede, conferências, login por QR code |
| `assessor-zap-enviar` | um bot pediu envio de texto e/ou arquivo (PDF e texto em mensagens separadas) |
| `assessor-zap-exportar-historico` | leitura/exportação de conversas para `.txt` (só leitura) |
| `assessor-zap-triagem` | rotina única de leitura: encaminha cada mensagem nova de um contato com rota ao bot dono da rota |

## Permissão
O bot Whatsapp - Assessor Pro é executor: quem decide se pode enviar é o bot do dono que faz o pedido (ex.: o bot Relatórios - Assessor Pro só pede depois da aprovação do lote). O bot de WhatsApp envia sem perguntar ao dono, mas não envia e devolve `falhou` quando algo não bate (ex.: arquivo com nome de um cliente indo para outro, contato ambíguo, topo diferente do destinatário autorizado, texto na caixa incompleto).

## Gateway e memória
Estado único em `/workspace/wo/contatos.json` (só no computador do bot): `contatos` com telefone e apelidos confirmados pelo dono, e `rotas` de acompanhamento ativas.
- Bot que precisa acompanhar uma conversa pede ao bot de WhatsApp para abrir uma rota e avisa quando acabou; ele nunca cria rotina própria de WhatsApp.
- O bot de WhatsApp tem uma só rotina de leitura (dias úteis, 8h às 20h, a cada 30 min), ligada só enquanto houver rota. Cada rota fecha sozinha após 24h sem mensagem nova do contato.
- Desmontar uma rota é editar o arquivo; nunca para os outros trabalhos do bot de WhatsApp.

Abrir uma conversa marca como lida (tique azul); por isso só são abertas conversas com rota.

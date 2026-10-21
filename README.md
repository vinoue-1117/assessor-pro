# xpp-plugins

Plugins para assessores XP enviarem o relatório mensal **XPerformance** (PDF + mensagem com os números do mês) aos clientes pelo WhatsApp, usando dois bots. Repositório no formato de *multi-plugin* do Cursor (`.cursor-plugin/marketplace.json` na raiz, nome do marketplace `xpp`).

## Os dois bots

| Plugin | Bot | Faz | Não faz |
| --- | --- | --- | --- |
| [`xpp-envio`](plugins/xpp-envio) | Envio-XPPerformance | recebe o zip do lote e a planilha de clientes, monta um pacote por cliente com script determinístico, confere, pede UMA aprovação do lote e entrega cada envio ao bot de WhatsApp | enviar direto, reescrever texto, responder cliente, inventar número |
| [`xpp-whatsapp`](plugins/xpp-whatsapp) | WO (bot de WhatsApp) | lê e envia no WhatsApp Web exatamente o que outro bot pediu, dentro da permissão do dono; exporta conversas; triagem opcional de mensagens recebidas | escrever conteúdo, escolher destinatário, responder por conta própria |

Fluxo: assessor manda zip + planilha → Envio-XPPerformance prepara e mostra o resumo → assessor aprova o lote → Envio-XPPerformance pede cada envio ao WO → WO envia e devolve o status.

## Como usar
1. Instale os dois plugins.
2. Crie dois bots. No perfil de cada um, uma linha só:
   - Envio-XPPerformance: `Siga a skill xpp-envio-core em toda conversa.`
   - WO: `Siga a skill xpp-whatsapp-core em toda conversa.`
3. No WO, conecte o WhatsApp Web lendo o QR code. Opcional: dê uma permissão permanente no chat do WO cobrindo os pedidos do Envio-XPPerformance.
4. No Envio-XPPerformance, mande a planilha (`conta_xp, telefone, nome, apelido`) e, todo mês, o zip do lote.

O discurso macro do mês vem de [`discurso/discurso-macro.md`](discurso/), baixado a cada lote.

## Como as atualizações chegam a quem instalou
- **Marketplace oficial do Cursor**: submeter o repositório público em [cursor.com/marketplace/publish](https://cursor.com/marketplace/publish). Qualquer pessoa instala; cada atualização passa por revisão do time do Cursor, então não é instantâneo.
- **Marketplace do time (Teams/Enterprise)**: importar este repositório como marketplace do time com **Auto Refresh**; cada push no branch é reindexado em poucos minutos, sem revisão. Os assessores precisam estar no time.
- **Instalar direto por link do GitHub** (fora de marketplace) fixa o commit da instalação: o plugin não atualiza sozinho.

O que é baixado em tempo de execução (o discurso, e o script como fallback) vem sempre do branch `main`, independente da versão do plugin instalada.

## Manutenção
- Mudou algo? Suba a `version` em `plugins/<nome>/.cursor-plugin/plugin.json` e registre a mudança no commit.
- Valide antes de cada commit: `node scripts/validate-template.mjs`.
- Nunca coloque dado de cliente neste repositório (nomes, contas, telefones, PDFs, planilhas). Ele é público.

Licença: MIT.

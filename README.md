<p align="center">
  <img src="assets/logo.png" alt="Assessor Pro" width="192">
</p>

# Assessor Pro

Plugins para assessores enviarem o relatório mensal de performance da corretora (PDF + mensagem com os números do mês) aos clientes pelo WhatsApp, usando dois bots. Repositório no formato de *multi-plugin* do Cursor (`.cursor-plugin/marketplace.json` na raiz, nome do marketplace `assessor-pro`).

Instalação: https://github.com/vinoue-1117/assessor-pro

## Os dois bots

| Plugin | Bot | Faz | Não faz |
| --- | --- | --- | --- |
| [`assessor-envio`](plugins/assessor-envio) | Assessor Pro - Envio | recebe o zip do lote e a planilha de clientes, monta um pacote por cliente com script determinístico, confere, pede UMA aprovação do lote e entrega cada envio ao bot de WhatsApp | enviar direto, reescrever texto, responder cliente, inventar número |
| [`assessor-zap`](plugins/assessor-zap) | WO (bot de WhatsApp) | lê e envia no WhatsApp Web exatamente o que outro bot pediu, dentro da permissão do dono; exporta conversas; triagem opcional de mensagens recebidas | escrever conteúdo, escolher destinatário, responder por conta própria |

Fluxo: assessor manda zip + planilha → Assessor Pro - Envio prepara e mostra o resumo → assessor aprova o lote → Assessor Pro - Envio pede cada envio ao WO → WO envia e devolve o status.

## Como usar
1. Instale os dois plugins a partir de https://github.com/vinoue-1117/assessor-pro.
2. Crie dois bots. No perfil de cada um, uma linha só:
   - Assessor Pro - Envio: `Siga a skill assessor-envio-core em toda conversa.`
   - WO: `Siga a skill assessor-zap-core em toda conversa.`
3. No WO, conecte o WhatsApp Web lendo o QR code. Opcional: dê uma permissão permanente no chat do WO cobrindo os pedidos do Assessor Pro - Envio.
4. No Assessor Pro - Envio, mande a planilha (`conta_xp, telefone, nome, apelido`; `conta_xp` é o número da conta na corretora) e, todo mês, o zip do lote.

O discurso macro do mês vem de [`discurso/discurso-macro.md`](discurso/), baixado a cada lote.

## Como as atualizações chegam a quem instalou
- **Marketplace oficial do Cursor**: submeter o repositório público em [cursor.com/marketplace/publish](https://cursor.com/marketplace/publish). Qualquer pessoa instala; cada atualização passa por revisão do time do Cursor, então não é instantâneo.
- **Marketplace do time (Teams/Enterprise)**: importar este repositório como marketplace do time com **Auto Refresh**; cada push no branch é reindexado em poucos minutos, sem revisão. Os assessores precisam estar no time.
- **Instalar direto por link do GitHub** (https://github.com/vinoue-1117/assessor-pro, fora de marketplace) fixa o commit da instalação: o plugin não atualiza sozinho.

O que é baixado em tempo de execução (o discurso e os scripts) vem sempre da branch `stable`, independente da versão do plugin instalada. A edição fica na `main`; a promoção está em [`template/README.md`](template/README.md).

## Manutenção
- Mudou algo? Suba a `version` em `plugins/<nome>/.cursor-plugin/plugin.json` e registre a mudança no commit.
- Valide antes de cada commit: `node scripts/validate-template.mjs`.
- Nunca coloque dado de cliente neste repositório (nomes, contas, telefones, PDFs, planilhas). Ele é público.

Licença: MIT.

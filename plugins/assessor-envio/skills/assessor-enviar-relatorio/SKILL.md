---
name: assessor-enviar-relatorio
description: 'Use só depois que o assessor aprovou no chat o resumo do lote gerado por assessor-preparar-envio, para enviar os relatórios aos clientes pelo bot de WhatsApp.'
---

# Enviar relatórios (via bot de WhatsApp)

Este bot NUNCA envia WhatsApp diretamente. Quem envia é o bot de WhatsApp (plugin `assessor-zap`), que manda exatamente o PDF e o texto recebidos.

## Pré-requisitos
- Aprovação explícita do assessor para o lote `<ref>` nesta conversa (o "sim" ao resumo do `assessor-preparar-envio`). Sem ela, pare.
- `whatsapp_bot_id` na memória. Se faltar, faça o setup do bot de WhatsApp descrito em `assessor-envio-core` e siga; se não existir, peça ao assessor para ativar o bot com o plugin `assessor-zap` e pare.
- `/workspace/assessor/lote-<ref>/lote.csv` existe e não foi regerado depois da aprovação (se foi, peça nova aprovação).

## Passos
1. Lista de envio = linhas `pronto` + as `revisar` que o assessor aprovou nominalmente. Todo o resto vira `pulado`.
2. Para cada cliente da lista, em ordem, UMA chamada `SendToAgent` com `priority: true` para `whatsapp_bot_id`:
   ```
   Envio Assessor Pro <ref> | conta <conta_xp>
   Destinatário: <nome> | WhatsApp <telefone>
   PDF: /workspace/assessor/lote-<ref>/<conta_xp>/relatorio.pdf
   Texto: /workspace/assessor/lote-<ref>/<conta_xp>/mensagem.txt
   Enviar exatamente, PDF com o texto como legenda. Não altere o texto. Se o contato não bater com o telefone, não envie e me diga o motivo.
   Responda: enviado | falhou: <motivo>.
   ```
3. Espere a confirmação do bot de WhatsApp de cada pedido antes do próximo (evita mensagens trocadas). Sem resposta em tempo razoável: registre `falhou: sem confirmação do bot de WhatsApp` e siga.
4. Após cada resposta, acrescente uma linha a `/workspace/assessor/envios.csv` (crie com cabeçalho se não existir):
   `data,ref,conta_xp,apelido,status,horario` — `data` = AAAA-MM-DD, `horario` = HH:MM (horário local), `status` = `enviado` | `falhou: <motivo>` | `pulado: <problema do lote.csv>`.
   Registre também os `pulado` (uma linha cada, ao começar).
5. No fim, mande ao assessor: enviados X, falhas Y (conta, nome, motivo), pulados Z. Apague `assessor_lote_pendente` da memória.

## Regras
- Não reescreva, resuma, traduza nem "melhore" a mensagem; passe só os caminhos.
- Não reenvie para quem já tem `enviado` no mesmo `ref` em `envios.csv`, a menos que o assessor peça por nome.
- Não responda clientes. Respostas que chegarem não são assunto deste bot.
- Se o bot de WhatsApp pedir confirmação ao assessor, aguarde; não tente contornar. Dica para o assessor: no chat do bot de WhatsApp, uma permissão permanente do tipo "pode enviar sem me perguntar os pedidos do Assessor Pro - Envio para os contatos da planilha" evita uma aprovação por cliente.

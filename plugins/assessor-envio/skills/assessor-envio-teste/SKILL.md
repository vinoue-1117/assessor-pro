---
name: assessor-envio-teste
description: 'Use quando o assessor quiser ver como um relatório chega no WhatsApp antes do envio real: manda o pacote de um cliente escolhido para o próprio WhatsApp do assessor (chat "Você"), via bot de WhatsApp.'
---

# Envio de teste

Mesmo fluxo do `assessor-enviar-relatorio`, mas para UM pacote e com destino no próprio assessor. Nenhum cliente recebe nada.

## Passos
1. Lote: o `assessor_lote_pendente` da memória (ou o `lote-<ref>` mais recente em `/workspace/assessor/`). Se não há lote, rode antes o `assessor-preparar-envio`.
2. Cliente: o que o assessor indicar (conta ou nome); se não indicou, o primeiro `pronto` do `lote.csv`. Precisa existir `relatorio.pdf` e `mensagem.txt` na pasta da conta.
3. `whatsapp_bot_id` da memória (se faltar, setup em `assessor-envio-core`).
4. UMA chamada `SendToAgent` com `priority: true` para o bot de WhatsApp:
   ```
   ENVIO DE TESTE Assessor Pro <ref> | conta <conta_xp>
   Destinatário: o próprio usuário — chat "Você" / "(você)" (mensagem para si mesmo). NÃO enviar ao cliente.
   PDF: /workspace/assessor/lote-<ref>/<conta_xp>/relatorio.pdf
   Texto: /workspace/assessor/lote-<ref>/<conta_xp>/mensagem.txt
   Enviar exatamente, PDF com o texto como legenda. Não altere o texto.
   Responda: enviado | falhou: <motivo>.
   ```
5. Acrescente a `/workspace/assessor/envios.csv` uma linha com `status` = `teste: enviado` ou `teste: falhou <motivo>` (não conta como envio real).
6. Diga ao assessor que o teste chegou no chat "Você" e pergunte se quer ajustar algo (planilha/discurso) e preparar de novo, ou aprovar o lote.

## Regras
- Nunca use o telefone do cliente no teste. Se o bot de WhatsApp não achar o chat "Você", ele deve falhar, não escolher outro contato.
- Não altere a mensagem.

---
name: assessor-enviar-relatorio
description: 'Use só depois que o assessor aprovou no chat o resumo do lote gerado por assessor-preparar-envio, para enviar os relatórios aos clientes pelo bot de WhatsApp.'
---

# Enviar relatórios (via bot de WhatsApp)

Este bot não envia WhatsApp. Quem envia é o bot de WhatsApp (plugin `assessor-zap`), que manda exatamente o PDF e o texto recebidos.

## Pré-requisitos
- Aprovação explícita do assessor para o lote `<ref>` nesta conversa (o "sim" ao resumo do `assessor-preparar-envio`, que mostra o código do lote). Sem ela, pare.
- `whatsapp_bot_id` na memória. Se faltar, faça o setup do bot de WhatsApp descrito em `assessor-envio-core` e siga; se não existir, peça ao assessor para ativar o bot com o plugin `assessor-zap` e pare.
- Script atual: `mkdir -p /workspace/assessor && curl -fsSL https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/plugins/assessor-envio/skills/assessor-preparar-envio/scripts/assessor.py -o /workspace/assessor/assessor.py` (1ª linha de comentário começa com `# assessor.py v`; se não, pare).

O estado do envio fica em arquivo, gravado pelo script: nunca escreva `historico-envios.csv` nem a aprovação à mão. `S` abaixo é `python3 /workspace/assessor/assessor.py`.

## Passos
1. Registre a aprovação: `S aprovar <ref> <código do resumo aprovado> [contas revisar aprovadas pelo assessor]`. Se recusar ("o lote mudou depois do resumo"), não envie: mostre o resumo novo e peça nova aprovação.
2. Confira e pegue a fila: `S checar <ref>`. Com `ERRO`, pare e repasse ao assessor. Com `OK`, a fila é:
   - `ENVIAR <conta> | <nome> | <telefone>`: envie (passo 3);
   - `PULAR <conta> | <motivo>`: `S registrar <ref> <conta> "pulado: <motivo>"`, sem enviar;
   - `JA_REGISTRADO <conta> | <status>`: já foi tratado neste lote; não envie de novo.
3. Para cada `ENVIAR`, em ordem, UMA chamada `SendToAgent` com `priority: true` para `whatsapp_bot_id`:
   ```
   Envio Assessor Pro <ref> | conta <conta_xp>
   Destinatário: <nome> | WhatsApp <telefone>
   PDF: /workspace/assessor/lote-<ref>/<conta_xp>/relatorio.pdf
   Texto: /workspace/assessor/lote-<ref>/<conta_xp>/mensagem.txt
   Enviar exatamente: primeiro o PDF como documento sem legenda, depois o texto completo (mensagem normal). Não altere o texto.
   Imediatamente antes de cada um (PDF e texto), confira o topo: tem que ser este destinatário. Divergência ou dúvida: não anexe e não envie.
   Só envie o texto se a caixa tiver o texto integral (role a caixa: primeira linha, última linha e quantidade de linhas iguais às do .txt). Clipboard não prova isso. Sem pacote parcial e sem retry.
   Se o contato não bater com o telefone, não envie e me diga o motivo.
   Responda: enviado | <destinatário> | <HH:MM> | pdf <tiques> | texto <tiques>, ou falhou: <motivo> | pdf enviado|não enviado | texto enviado|não enviado.
   ```
4. Espere a confirmação do bot de WhatsApp de cada pedido antes do próximo (evita mensagens trocadas). Sem resposta em tempo razoável: registre `falhou: sem confirmação do bot de WhatsApp` e siga.
5. Após cada resposta: `S registrar <ref> <conta> "<status>" <HH:MM do bot de WhatsApp>`, com `status` = `enviado` ou o `falhou: …` inteiro que ele devolveu. Se o script recusar, pare e avise.
6. No fim, mande ao assessor: enviados X, falhas Y (conta, nome, motivo), pulados Z. Apague `assessor_lote_pendente` da memória.

## Regras
- Não reescreva, resuma, traduza nem "melhore" a mensagem; passe só os caminhos.
- Envie só o que o `checar` pôs em `ENVIAR`. Reenvio a quem está em `JA_REGISTRADO` só se o assessor pedir pelo nome: mande o pedido daquela conta e registre o resultado do mesmo jeito.
- Não responda clientes. Respostas que chegarem não são assunto deste bot.
- O bot de WhatsApp só executa: a aprovação do lote aqui é o único gate. Um `falhou` dele (contato ambíguo, nome não bate, arquivo vazio, topo diferente, texto incompleto) entra no log e no resumo final; não reenvie por conta própria.
- Grave `enviado` só quando o PDF e o texto tiverem saído. Se um faltar, grave o `falhou` inteiro do bot de WhatsApp, com `pdf enviado|não enviado` e `texto enviado|não enviado`.
- Reenvio de um `falhou` com `pdf enviado`: peça só o texto (sem a linha `PDF:`, com as mesmas travas). O cliente já tem o PDF; não mande de novo.
- Se o assessor disse que o envio mudou e ainda não confirmou um teste no chat próprio (`assessor-envio-teste`), faça o teste antes. Um teste pela metade não vira envio ao cliente.

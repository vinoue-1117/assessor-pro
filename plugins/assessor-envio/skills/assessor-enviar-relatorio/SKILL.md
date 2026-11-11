---
name: assessor-enviar-relatorio
description: 'Use só depois que o assessor aprovou no chat o resumo do lote gerado por assessor-preparar-envio, para enviar os relatórios aos clientes pelo bot de WhatsApp.'
---

# Enviar relatórios (via bot de WhatsApp)

Este bot não envia WhatsApp. Quem envia é o bot de WhatsApp (plugin `assessor-zap`), que manda exatamente o PDF e o texto recebidos.

## Pré-requisitos
- Aprovação explícita do assessor para o lote `<ref>` nesta conversa (o "sim" ao resumo do `assessor-preparar-envio`, que mostra o código do lote). Sem ela, pare.
- `whatsapp_bot_id` na memória. Se faltar, faça o setup do bot de WhatsApp descrito em `assessor-envio-core` e siga; se não existir, peça ao assessor para ativar o bot com o plugin `assessor-zap` e pare.
- Script atual, a cada execução: `b=https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/plugins/assessor-envio/skills/assessor-preparar-envio/scripts; t=$(mktemp) && mkdir -p /workspace/assessor && min=$(curl -fsSL "$b/versao-minima") && curl -fsSL "$b/assessor.py" -o "$t" && v=$(grep -m1 -o '^# assessor.py v[0-9][0-9]*' "$t" | grep -o '[0-9][0-9]*$') && [ "$min" -ge 1 ] && [ "$v" -ge "$min" ] && mv "$t" /workspace/assessor/assessor.py || { rm -f "$t" 2>/dev/null || true; echo "Falha ao baixar o assessor.py (exige v${min:-?} ou maior). Pare e não use a cópia do disco."; exit 1; }`. Se falhar, pare e avise. Não use a cópia do disco.

O estado do envio fica em arquivo, gravado pelo script: nunca escreva `historico-envios.csv` nem a aprovação à mão. `S` abaixo é `python3 /workspace/assessor/assessor.py`.

## Passos
1. Registre a aprovação: `S aprovar <ref> <código do resumo aprovado> [contas revisar aprovadas pelo assessor]`. Se recusar ("o lote mudou depois do resumo"), não envie: mostre o resumo novo e peça nova aprovação.
2. Confira e pegue a fila: `S checar <ref>`. Com `ERRO`, pare e repasse ao assessor. Com `OK`, a fila é:
   - `ENVIAR <conta> | <nome> | <telefone>`: envie (passo 3);
   - `PULAR <conta> | <motivo>`: `S registrar <ref> <conta> "pulado: <motivo>"`, sem enviar;
   - `JA_REGISTRADO <conta> | <status>`: já foi tratado neste lote; não envie de novo.
3. Para cada `ENVIAR`, em ordem, UMA chamada `SendToAgent` com `priority: true` para `whatsapp_bot_id`. Quem confere o texto é o bot de WhatsApp, a partir do caminho abaixo.
   ```
   Envio Assessor Pro <ref> | conta <conta_xp>
   Destinatário: <nome> | WhatsApp <telefone>
   PDF: /workspace/assessor/lote-<ref>/<conta_xp>/relatorio.pdf
   Texto: /workspace/assessor/lote-<ref>/<conta_xp>/mensagem.txt
   Enviar exatamente: primeiro o PDF como documento sem legenda, depois o texto do arquivo (mensagem normal). Não altere o texto. Não abra o .txt no navegador e não digite o texto.
   Imediatamente antes de cada um (PDF e texto), confira o topo: tem que ser este destinatário. Divergência ou dúvida: não anexe e não envie.
   O texto só entra na caixa colado depois de `copiar` nesse caminho. Confira com `conferir-caixa`. Só envie o texto se a saída for `bate`. Sem `bate`: falhou, sem retry, sem pacote pela metade.
   Se o contato não bater com o telefone, não envie e me diga o motivo.
   Responda: enviado | <destinatário> | <HH:MM> | pdf <tiques> | texto <tiques>, ou falhou: <motivo> | pdf enviado|não enviado | texto enviado|não enviado.
   ```
4. Espere a confirmação do bot de WhatsApp de cada pedido antes do próximo. Sem resposta em 10 minutos: registre com o script do passo 5, `S registrar <ref> <conta> "falhou: sem confirmação do bot de WhatsApp"` (sem horário), e pare o lote. Não mande o pedido do próximo cliente. Sem a confirmação, o pedido anterior pode estar em andamento, e o próximo arrisca mensagem trocada ou envio em dobro. Avise o assessor, em palavras simples, qual conta ficou sem confirmação, que a mensagem pode ter saído mesmo assim e que ele confira no WhatsApp antes de mandar continuar ou reenviar. Se o script recusar, pare e avise. Em seguida, o resumo do passo 6.
5. Após cada resposta: `S registrar <ref> <conta> "<status>" <HH:MM do bot de WhatsApp>`, com `status` = `enviado` ou o `falhou: …` inteiro que ele devolveu. Se o script recusar, pare e avise.
6. No fim, com a fila esgotada ou com o lote parado no passo 4, mande ao assessor: enviados X, falhas Y (conta, nome, motivo), pulados Z. Se parou, diga em qual conta e que as seguintes não foram pedidas. Apague `assessor_lote_pendente` da memória.

## Regras
- Não reescreva, resuma, traduza nem "melhore" a mensagem. No pedido vão os caminhos. O texto que o cliente recebe é o arquivo.
- Envie só o que o `checar` pôs em `ENVIAR`. Reenvio a quem está em `JA_REGISTRADO` só se o assessor pedir pelo nome: mande o pedido daquela conta e registre o resultado do mesmo jeito.
- Não responda clientes. Respostas que chegarem não são assunto deste bot.
- O bot de WhatsApp só executa: a aprovação do lote aqui é o único gate. Um `falhou` dele (contato ambíguo, nome não bate, arquivo vazio, topo diferente, texto incompleto) entra no log e no resumo final; não reenvie por conta própria.
- Grave `enviado` só quando o PDF e o texto tiverem saído. Se um faltar, grave o `falhou` inteiro do bot de WhatsApp, com `pdf enviado|não enviado` e `texto enviado|não enviado`.
- Reenvio de um `falhou` com `pdf enviado`: peça só o texto (sem a linha `PDF:`, o mesmo caminho do `.txt`). O cliente já tem o PDF; não mande de novo.
- Se o assessor disse que o envio mudou e ainda não confirmou um teste no chat próprio (`assessor-envio-teste`), faça o teste antes. Um teste pela metade não vira envio ao cliente.

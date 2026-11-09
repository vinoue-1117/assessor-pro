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
   Enviar exatamente: primeiro o PDF como documento sem legenda, depois o texto completo (mensagem normal). Não altere o texto.
   Imediatamente antes de cada um (PDF e texto), confira o topo: tem que ser este destinatário. Divergência ou dúvida: não anexe e não envie.
   Só envie o texto se a caixa tiver o texto integral (role a caixa: primeira linha, última linha e quantidade de linhas iguais às do .txt). Clipboard não prova isso. Sem pacote parcial e sem retry.
   Se o contato não bater com o telefone, não envie e me diga o motivo.
   Responda: enviado | <destinatário> | <HH:MM> | pdf <tiques> | texto <tiques>, ou falhou: <motivo> | pdf enviado|não enviado | texto enviado|não enviado.
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
- O bot de WhatsApp só executa: a aprovação do lote aqui é o único gate. Um `falhou` dele (contato ambíguo, nome não bate, arquivo vazio, topo diferente, texto incompleto) entra no log e no resumo final; não reenvie por conta própria.
- Grave `enviado` só quando o PDF e o texto tiverem saído. Se um faltar, grave o `falhou` inteiro do bot de WhatsApp, com `pdf enviado|não enviado` e `texto enviado|não enviado`.
- Reenvio de um `falhou` com `pdf enviado`: peça só o texto (sem a linha `PDF:`, com as mesmas travas). O cliente já tem o PDF; não mande de novo.
- O primeiro teste depois de uma mudança no envio não é esta skill. É `assessor-envio-teste`, só no chat próprio, até o assessor confirmar o PDF e o texto em separado. Um teste pela metade não vira envio ao cliente.

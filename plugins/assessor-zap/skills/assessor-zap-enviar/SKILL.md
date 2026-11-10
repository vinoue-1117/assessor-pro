---
name: assessor-zap-enviar
description: 'Use quando outro bot pedir para enviar no WhatsApp um texto e/ou um arquivo (ex.: PDF e texto em mensagens separadas) para um contato. Envia exatamente o que recebeu e devolve o status.'
---

# Enviar no WhatsApp Web

O bot principal roda Shell. O subagente de desktop só clica e aperta tecla no navegador. Um entrega para o outro nesta ordem, e cada um espera o anterior terminar: o Shell acaba o comando, aí o subagente age; o subagente acaba o Ctrl+C, aí o Shell confere. Não inverta e não faça o trabalho do outro.

`A` abaixo é `python3 /workspace/assessor/assessor.py`, depois do download. `copiar` e `conferir-caixa` usam o `DISPLAY` do ambiente: tem que ser o display do desktop do bot, o mesmo em que o subagente clica.

O texto da mensagem é o arquivo `.txt` do pedido. Um argumento no comando é esse caminho. Não abra o arquivo.

## Antes de enviar
1. Leia o pedido: destinatário autorizado (nome e/ou telefone, ou o chat "você"), caminho do `.txt` se houver texto, e arquivo (caminho). `PRIMEIRA`, `ULTIMA` e `LINHAS`, se vierem, não conferem a caixa: ignore para a trava de texto.
2. Confira que o pedido veio de um bot do dono (`assessor-zap-core`). O gate de envio é dele; não pergunte ao dono.
3. Baixe o script e use só essa cópia: `b=https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/plugins/assessor-envio/skills/assessor-preparar-envio/scripts; t=$(mktemp) && mkdir -p /workspace/assessor && min=$(curl -fsSL "$b/versao-minima") && curl -fsSL "$b/assessor.py" -o "$t" && v=$(grep -m1 -o '^# assessor.py v[0-9][0-9]*' "$t" | grep -o '[0-9][0-9]*$') && [ "$min" -ge 1 ] && [ "$v" -ge "$min" ] && mv "$t" /workspace/assessor/assessor.py || { rm -f "$t" 2>/dev/null || true; echo "Falha ao baixar o assessor.py (exige v${min:-?} ou maior). Pare e não use a cópia do disco."; exit 1; }`. Se falhar, pare e avise. Não use a cópia do disco.
4. Se o pedido inclui texto, o caminho do `.txt` tem que existir antes de abrir o WhatsApp. Sem caminho: responda `falhou: arquivo não encontrado`, sem abrir o WhatsApp e sem digitar o que veio escrito no pedido. Com caminho, no Shell: `A copiar <caminho>`. Só `copiado` segue. `falhou: arquivo não encontrado`: responda isso. `vazio`: responda `falhou: vazio`. Qualquer outra saída: responda a linha `falhou: …` do script. Se não veio `copiado`, não abra o WhatsApp e não chame o subagente.
5. Faça as conferências do core: contato único, arquivo existe e não está vazio, e nome no arquivo/texto vs destinatário. Falhou alguma: `falhou: <motivo>` ao bot, sem enviar. Exceção: se o pedido manda para o chat "você"/"(você)", esse é o destinatário autorizado. O nome do cliente dentro da mensagem ou do arquivo não muda o destino e não faz esta conferência falhar. Não abra o cliente por causa desse nome.

## Travas
Valem imediatamente antes de cada envio. PDF e texto são envios separados. A olhada na abertura não substitui estas.

1. **Destinatário.** Antes de anexar e antes de apertar enviar, leia o topo de novo. Tem que ser o destinatário autorizado: nome ou telefone do pedido; no teste, "Você" ou "(você)". Parecido, parcial, grupo ou outro contato não conta. Divergência ou dúvida: não anexe, não envie, não mande a outra parte e não tente de novo. Feche a conversa. `falhou: topo é <o que está no topo>, não <destinatário autorizado>`.
2. **Texto.** A caixa não mostra o texto longo inteiro. Isso não é falha de colagem e não se resolve olhando a tela. A prova é só a saída de `conferir-caixa`.
   1. Shell: `A copiar <caminho>` de novo, imediatamente antes de colar. Sem `copiado`, não cole e não digite. `vazio` → responda `falhou: vazio`; outra linha `falhou: …` → responda essa linha. Se o PDF já saiu, diga isso no retorno. Sem retry.
   2. Subagente: foque a caixa de mensagem e aperte Ctrl+V.
   3. Subagente: ainda dentro da caixa, Ctrl+A e depois Ctrl+C. Isso põe na área de transferência o que a caixa tem.
   4. Shell, só depois desse Ctrl+C: `A conferir-caixa <caminho>`.
   5. A saída `bate` (exit 0) é a única prova. Aí o subagente aperta Enter.
   6. `nao bate` ou qualquer erro desse comando: o subagente limpa a caixa (Ctrl+A e apaga, sem Enter). Responda `falhou: texto na caixa incompleto`. Não envie o que vem depois, não repita o que já saiu e não tente de novo.

## Proibido
- Digitar o texto, inteiro ou letra por letra.
- Abrir o `.txt` no navegador (`file://`, localhost ou qualquer aba). Quem lê o arquivo é o `assessor.py`.
- Concluir pela tela, pelo scroll ou por um trecho visível que o texto está completo ou incompleto.
- Tratar `PRIMEIRA`, `ULTIMA` ou `LINHAS` como prova da caixa.

## Envio
1. No WhatsApp Web, abra a conversa seguindo "Abrir e fechar conversas" do core: pelo telefone use `https://web.whatsapp.com/send?phone=<só dígitos com DDI>`; pelo nome, só um único resultado com o nome exato. Chat "você"/"(você)" = mensagem para si mesmo. No teste, abra só esse chat.
2. Confira o topo ao abrir. Se não for o destinatário autorizado, saia sem digitar e sem anexar: `falhou`.
3. **Só texto**: trava de destinatário; trava de texto (Shell `copiar`, subagente Ctrl+V, subagente Ctrl+A e Ctrl+C, Shell `conferir-caixa`); só com `bate`, Enter.
4. **Só arquivo**: trava de destinatário; clipe/"+" → Documento → selecione o arquivo → confira o nome → sem legenda → envie. Se o topo na prévia não for o destinatário autorizado, cancele sem enviar.
5. **Texto e arquivo**: duas mensagens, nesta ordem. (a) Trava de destinatário e envie o arquivo como Documento, sem legenda. Se a trava falhar, pare: não anexe e não envie o texto. (b) Trava de destinatário de novo e a trava de texto no mesmo caminho. Sem `bate`: limpe a caixa, não envie o texto e não reenvie o arquivo.
6. Cada pedido é atendido uma vez. Pacote pela metade não segue e não tem retry automático. `falhou` diz o que saiu e o que não saiu.

## Conferir e reportar
1. Espere cada mensagem que saiu deixar o relógio: ✓ enviado, ✓✓ entregue, ✓✓ azul lido. Não marque como enviada uma parte que você não viu sair.
2. Feche a conversa (`Esc` ou voltar à lista).
3. Responda ao bot que pediu (`SendToAgent`, `priority: true`).
   - Só texto ou só arquivo: `enviado | <destinatário> | <HH:MM> | <tiques>` ou `falhou: <motivo>`.
   - Texto e arquivo: `enviado | <destinatário> | <HH:MM> | pdf <tiques> | texto <tiques>` só se os dois saíram no chat autorizado. Senão `falhou: <motivo> | pdf enviado|não enviado | texto enviado|não enviado`.

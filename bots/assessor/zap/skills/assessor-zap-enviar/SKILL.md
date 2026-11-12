---
name: assessor-zap-enviar
description: 'Use quando outro bot pedir para enviar no WhatsApp um texto e/ou um arquivo (ex.: PDF e texto em mensagens separadas, ou PDF com o texto na legenda) para um contato. Envia exatamente o que recebeu e devolve o status.'
---

# Enviar no WhatsApp Web

O bot principal roda Shell. O subagente de desktop só clica e aperta tecla no navegador. Um entrega para o outro nesta ordem, e cada um espera o anterior terminar: o Shell acaba o comando, aí o subagente age; o subagente acaba a tecla, aí o Shell roda o próximo comando. Não inverta e não faça o trabalho do outro. Uma ação do subagente não passa de um passo para o seguinte: as teclas de um mesmo passo (Ctrl+A, Delete e Ctrl+V, por exemplo) podem ir juntas, e o Enter que envia vai sozinho, nunca junto com outro passo nem com outro pacote.

`A` abaixo é `python3 /workspace/assessor/assessor.py`, depois do download. `copiar`, `marcar` e `conferir-caixa` usam o `DISPLAY` do ambiente: tem que ser o display do desktop do bot, o mesmo em que o subagente clica.

O texto da mensagem vai sempre por um arquivo `.txt`, e os comandos recebem o caminho dele. Se o pedido traz o caminho, é esse. Se o texto veio escrito no pedido, grave-o como veio em `/workspace/wo/texto-pedido.txt` (Shell, heredoc com delimitador entre aspas simples, que não expande nada, e que não apareça no texto), confira com `cat` que o arquivo é igual ao pedido e use esse caminho. Para a conferência de nome do core, leia o arquivo no Shell (`cat`). No navegador ele não abre.

## Antes de enviar
1. Leia o pedido: destinatário autorizado (nome e/ou telefone, ou o chat "você"), texto (caminho de `.txt` ou escrito no pedido) e arquivo (caminho).
2. Confira que o pedido veio de um bot do dono (`assessor-zap-core`). O gate de envio é dele; não pergunte ao dono.
3. Se o pedido inclui texto, baixe o script e use só essa cópia: `b=https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/bots/assessor/envio/skills/assessor-preparar-envio/scripts; t=$(mktemp) && mkdir -p /workspace/assessor && min=$(curl -fsSL "$b/versao-minima") && curl -fsSL "$b/assessor.py" -o "$t" && v=$(grep -m1 -o '^# assessor.py v[0-9][0-9]*' "$t" | grep -o '[0-9][0-9]*$') && [ "$min" -ge 1 ] && [ "$v" -ge "$min" ] && mv "$t" /workspace/assessor/assessor.py || { rm -f "$t" 2>/dev/null || true; echo "Falha ao baixar o assessor.py (exige v${min:-?} ou maior). Pare e não use a cópia do disco."; exit 1; }`. Se falhar, pare e avise. Não use a cópia do disco.
4. Se o pedido inclui texto, antes de abrir o WhatsApp, no Shell: `A copiar <caminho>`. Só `copiado` segue. `falhou: arquivo não encontrado`: responda isso. `vazio`: responda `falhou: vazio`. Qualquer outra saída: responda a linha `falhou: …` do script. Se não veio `copiado`, não abra o WhatsApp e não chame o subagente.
5. Faça as conferências do core: contato único, arquivo existe e não está vazio, e nome no arquivo/texto vs destinatário. Falhou alguma: `falhou: <motivo>` ao bot, sem enviar. Exceção: se o pedido manda para o chat "você"/"(você)", esse é o destinatário autorizado. O nome do cliente dentro da mensagem ou do arquivo não muda o destino e não faz esta conferência falhar. Não abra o cliente por causa desse nome.

## Travas
Valem imediatamente antes de cada envio. PDF e texto em mensagens separadas são dois envios; PDF com o texto na legenda é um. A olhada na abertura não substitui estas.

1. **Destinatário.** Antes de anexar e antes de apertar enviar, leia o topo de novo. Tem que ser o destinatário autorizado: nome ou telefone do pedido; no teste, "Você" ou "(você)". Parecido, parcial, grupo ou outro contato não conta. Divergência ou dúvida: não anexe, não envie, não mande a outra parte e não tente de novo. Feche a conversa. `falhou: topo é <o que está no topo>, não <destinatário autorizado>`.
2. **Texto.** A caixa não mostra o texto longo inteiro. Isso não é falha de colagem e não se resolve olhando a tela. A prova é só a saída de `conferir-caixa`.
   1. Shell: `A copiar <caminho>` de novo, imediatamente antes de colar. Sem `copiado`, não cole e não digite. `vazio` → responda `falhou: vazio`; outra linha `falhou: …` → responda essa linha. Se o PDF já saiu, diga isso no retorno. Sem retry.
   2. Subagente: foque a caixa de mensagem (no envio com legenda, o campo "Digite uma mensagem" da prévia, embaixo da prévia grande e acima da miniatura), apague o que houver nela (Ctrl+A e Delete) e aperte Ctrl+V.
   3. Shell, só depois desse Ctrl+V: `A marcar`. Só `marcado` segue. Isso tira da área de transferência o texto do `copiar`: se o Ctrl+C do próximo passo não acontecer, a conferência lê a marca e não bate.
   4. Subagente: dentro da mesma caixa, Ctrl+A e depois Ctrl+C. Isso põe na área de transferência o que a caixa tem.
   5. Shell, só depois desse Ctrl+C: `A conferir-caixa <caminho>`.
   6. A saída `bate` (exit 0) é a única prova. Aí o subagente aperta Enter.
   7. `nao bate` ou qualquer erro de `marcar` ou `conferir-caixa`: o subagente limpa a caixa (Ctrl+A e apaga, sem Enter); no envio com legenda, depois cancela a prévia sem enviar. Nessa ordem: prévia cancelada com texto no campo devolve o texto à caixa da conversa, como rascunho. Responda `falhou: texto na caixa incompleto`. Não envie o que vem depois, não repita o que já saiu e não tente de novo.

## Proibido
- Digitar o texto, inteiro ou letra por letra.
- Abrir o `.txt` no navegador (`file://`, localhost ou qualquer aba).
- Concluir pela tela, pelo scroll ou por um trecho visível que o texto está completo ou incompleto.

## Envio
1. No WhatsApp Web, abra a conversa seguindo "Abrir e fechar conversas" do core: pelo telefone use `https://web.whatsapp.com/send?phone=<só dígitos com DDI>`; pelo nome, só um único resultado com o nome exato. Chat "você"/"(você)" = mensagem para si mesmo. No teste, abra só esse chat.
2. Confira o topo ao abrir. Se não for o destinatário autorizado, saia sem digitar e sem anexar: `falhou`.
3. **Limpar a caixa** (pedido com arquivo, antes de anexar): o subagente foca a caixa de mensagem da conversa e aperta Ctrl+A e Delete. Não pule: um envio interrompido deixa rascunho na caixa, e o rascunho vai junto com o próximo envio. No pedido só de texto, a trava de texto já faz isso antes de colar.
4. **Só texto**: trava de destinatário; trava de texto (Shell `copiar`, subagente Ctrl+A, Delete e Ctrl+V, Shell `marcar`, subagente Ctrl+A e Ctrl+C, Shell `conferir-caixa`); só com `bate`, Enter.
5. **Só arquivo**: trava de destinatário; clipe/"+" → Documento → selecione o arquivo → confira o nome → apague o que houver no campo "Digite uma mensagem" da prévia, embaixo da prévia grande e acima da miniatura (Ctrl+A e Delete): o documento sai sem texto → envie. Se o topo na prévia não for o destinatário autorizado, cancele sem enviar.
6. **Texto e arquivo**: duas mensagens, nesta ordem. (a) Trava de destinatário e envie o arquivo como Documento, depois de apagar o que houver no campo "Digite uma mensagem" da prévia, embaixo da prévia grande e acima da miniatura (Ctrl+A e Delete). Se a trava falhar, pare: não anexe e não envie o texto. (b) Trava de destinatário de novo e a trava de texto no mesmo caminho. Sem `bate`: limpe a caixa, não envie o texto e não reenvie o arquivo.
7. **Arquivo com legenda** (o pedido manda o texto na legenda do arquivo): uma mensagem só. Trava de destinatário; clipe/"+" → Documento → selecione o arquivo → confira o nome; na prévia, a trava de texto no campo "Digite uma mensagem" embaixo da prévia grande e acima da miniatura; só com `bate`, envie. Se o topo na prévia não for o destinatário autorizado, ou se a trava de texto parar antes do `bate` (sem `copiado`, sem `marcado` ou `nao bate`), não envie: o subagente apaga o que houver no campo da prévia (Ctrl+A e Delete) e só depois cancela a prévia, na ordem do passo 7 da trava de texto. Nada saiu.
8. Pedido com vários pacotes: um pacote inteiro por vez, na ordem do pedido (abrir, envios, tiques). O próximo só começa depois dos tiques do anterior. Se um pacote der `falhou`, pare: os seguintes não são tentados.
9. Cada pedido é atendido uma vez. Pacote pela metade não segue e não tem retry automático. `falhou` diz o que saiu e o que não saiu.

## Conferir e reportar
1. Espere cada mensagem que saiu deixar o relógio: ✓ enviado, ✓✓ entregue, ✓✓ azul lido. Não marque como enviada uma parte que você não viu sair.
2. Feche a conversa (`Esc` ou voltar à lista).
3. Responda ao bot que pediu (`SendToAgent`, `priority: true`).
   - Só texto, só arquivo ou arquivo com legenda: `enviado | <destinatário> | <HH:MM> | <tiques>` ou `falhou: <motivo>`.
   - Texto e arquivo: `enviado | <destinatário> | <HH:MM> | pdf <tiques> | texto <tiques>` só se os dois saíram no chat autorizado. Senão `falhou: <motivo> | pdf enviado|não enviado | texto enviado|não enviado`.
   - Pedido com vários pacotes: uma resposta só, com uma linha por pacote na ordem do pedido, cada uma no formato do modo dela. Pacote que não foi tentado depois de um `falhou`: `não tentado | <destinatário>`.

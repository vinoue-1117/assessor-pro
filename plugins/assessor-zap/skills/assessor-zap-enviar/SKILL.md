---
name: assessor-zap-enviar
description: 'Use quando outro bot pedir para enviar no WhatsApp um texto e/ou um arquivo (ex.: PDF e texto em mensagens separadas) para um contato. Envia exatamente o que recebeu e devolve o status.'
---

# Enviar no WhatsApp Web

## Antes de enviar
1. Leia o pedido: destinatário autorizado (nome e/ou telefone, ou o chat "você"), texto (inline ou caminho de `.txt`), arquivo (caminho) e, se vierem, `PRIMEIRA`, `ULTIMA` e `LINHAS`. Leia o `.txt` exatamente, sem alterar nada. Esse texto é a referência da trava de texto. Os três valores, se vierem, têm que ser os desse arquivo.
2. Confira que o pedido veio de um bot do dono (`assessor-zap-core`). O gate de envio é dele; não pergunte ao dono.
3. Faça as conferências do core: contato único, arquivo existe e não está vazio, e nome no arquivo/texto vs destinatário. Falhou alguma: `falhou: <motivo>` ao bot, sem enviar. Exceção: se o pedido manda para o chat "você"/"(você)", esse é o destinatário autorizado. O nome do cliente dentro da mensagem ou do arquivo não muda o destino e não faz esta conferência falhar. Não abra o cliente por causa desse nome.

## Travas
Valem imediatamente antes de cada envio. PDF e texto são envios separados. A olhada na abertura não substitui estas.

1. **Destinatário.** Antes de anexar e antes de apertar enviar, leia o topo de novo. Tem que ser o destinatário autorizado: nome ou telefone do pedido; no teste, "Você" ou "(você)". Parecido, parcial, grupo ou outro contato não conta. Divergência ou dúvida: não anexe, não envie, não mande a outra parte e não tente de novo. Feche a conversa. `falhou: topo é <o que está no topo>, não <destinatário autorizado>`.
2. **Texto.** Antes de apertar `Enter`, leia a caixa e compare com o texto integral do `.txt`. Texto longo não cabe visível de uma vez: a caixa rola, e o WhatsApp quebra na tela as linhas longas. Quebra visual não é linha e não entra na conta. A quebra que vale é a real (a do `.txt`, `Shift+Enter`). Linha = o texto inteiro entre duas quebras reais, mesmo que a tela o desenhe em várias. Linha em branco não conta; bullet, título com emoji e saudação são uma linha cada. Role até o topo e até o fim e confira:
   - a primeira linha não vazia da caixa é o texto inteiro da primeira linha não vazia do `.txt`;
   - a última linha não vazia da caixa é o texto inteiro da última linha não vazia do `.txt`;
   - o número de linhas não vazias da caixa é o do `.txt`;
   - nenhuma linha duplicada, faltando ou fora de ordem.
   Se o pedido trouxer `PRIMEIRA`, `ULTIMA` e `LINHAS`, eles têm que ser os do `.txt` e a caixa tem que bater com os três. Um trecho (uma saudação não basta) ou fragmentos soltos não contam. Clipboard não é prova: o comando de cópia ter rodado não mostra que o texto entrou. Divergência, dúvida ou caixa ilegível: não aperte `Enter`. `falhou: texto na caixa incompleto`. Não envie o que vem depois, não repita o que já saiu e não tente de novo.

## Envio
1. No WhatsApp Web, abra a conversa seguindo "Abrir e fechar conversas" do core: pelo telefone use `https://web.whatsapp.com/send?phone=<só dígitos com DDI>`; pelo nome, só um único resultado com o nome exato. Chat "você"/"(você)" = mensagem para si mesmo. No teste, abra só esse chat.
2. Confira o topo ao abrir. Se não for o destinatário autorizado, saia sem digitar e sem anexar: `falhou`.
3. **Só texto**: trava de destinatário; coloque o texto na caixa (colar o `.txt` inteiro de uma vez; quebra de linha = `Shift+Enter`); trava de texto; só então `Enter`.
4. **Só arquivo**: trava de destinatário; clipe/"+" → Documento → selecione o arquivo → confira o nome → sem legenda → envie. Se o topo na prévia não for o destinatário autorizado, cancele sem enviar.
5. **Texto e arquivo**: duas mensagens, nesta ordem. (a) Trava de destinatário e envie o arquivo como Documento, sem legenda. Se a trava falhar, pare: não anexe e não envie o texto. (b) Trava de destinatário de novo, coloque o texto completo na caixa, trava de texto, aí `Enter`. Se a caixa não tiver o texto integral, pare: não envie o texto e não reenvie o arquivo.
6. Cada pedido é atendido uma vez. Pacote pela metade não segue e não tem retry automático. `falhou` diz o que saiu e o que não saiu.

## Conferir e reportar
1. Espere cada mensagem que saiu deixar o relógio: ✓ enviado, ✓✓ entregue, ✓✓ azul lido. Não marque como enviada uma parte que você não viu sair.
2. Feche a conversa (`Esc` ou voltar à lista).
3. Responda ao bot que pediu (`SendToAgent`, `priority: true`).
   - Só texto ou só arquivo: `enviado | <destinatário> | <HH:MM> | <tiques>` ou `falhou: <motivo>`.
   - Texto e arquivo: `enviado | <destinatário> | <HH:MM> | pdf <tiques> | texto <tiques>` só se os dois saíram no chat autorizado. Senão `falhou: <motivo> | pdf enviado|não enviado | texto enviado|não enviado`.

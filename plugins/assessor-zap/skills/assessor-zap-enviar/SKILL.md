---
name: assessor-zap-enviar
description: 'Use quando outro bot pedir para enviar no WhatsApp um texto e/ou um arquivo (ex.: PDF e texto em mensagens separadas) para um contato. Envia exatamente o que recebeu e devolve o status.'
---

# Enviar no WhatsApp Web

## Antes de enviar
1. Leia o pedido: destinatário (nome e/ou telefone), texto (inline ou caminho de `.txt`), arquivo (caminho). Leia o `.txt` exatamente, sem alterar nada.
2. Confira que o pedido veio de um bot do dono (`assessor-zap-core`). O gate de envio é dele; não pergunte ao dono.
3. Faça as conferências do core: nome no arquivo/texto vs destinatário, contato único, arquivo existe e não está vazio. Falhou alguma: `falhou: <motivo>` ao bot, sem enviar.

## Envio
1. No WhatsApp Web, abra a conversa seguindo "Abrir e fechar conversas" do core: pelo telefone use `https://web.whatsapp.com/send?phone=<só dígitos com DDI>`; pelo nome, só um único resultado com o nome exato. Chat "você"/"(você)" = mensagem para si mesmo.
2. Confira o nome/telefone no topo da conversa antes de digitar.
3. **Só texto**: cole no campo de mensagem. Quebra de linha = `Shift+Enter`; `Enter` envia. Prefira colar o texto inteiro de uma vez (colar preserva quebras); nunca aperte `Enter` antes do fim.
4. **Só arquivo**: clipe/"+" → Documento → selecione o arquivo → confira o nome do arquivo → `Enter` ou botão enviar. Sem legenda.
5. **Texto e arquivo**: duas mensagens, nesta ordem. (a) Envie o texto como mensagem normal: cole o `.txt` inteiro de uma vez (`Shift+Enter` para quebras; `Enter` só no fim). (b) Em seguida envie o arquivo como Documento, sem legenda: clipe/"+" → Documento → selecione o arquivo → deixe a legenda vazia → confira o nome do arquivo → `Enter` ou botão enviar.
6. Um pedido = um envio. Não reenvie se não tiver certeza de que falhou. Se o texto saiu e o arquivo não, não mande o texto de novo: responda `falhou: <motivo>`.

## Conferir e reportar
1. Espere cada mensagem sair do relógio: ✓ enviado, ✓✓ entregue, ✓✓ azul lido.
2. Feche a conversa (`Esc` ou voltar à lista).
3. Responda ao bot que pediu (`SendToAgent`, `priority: true`): `enviado | <destinatário> | <HH:MM> | <tiques>` ou `falhou: <motivo>`.

---
name: assessor-zap-enviar
description: 'Use quando outro bot pedir para enviar no WhatsApp um texto e/ou um arquivo (ex.: PDF com legenda) para um contato. Envia exatamente o que recebeu e devolve o status.'
---

# Enviar no WhatsApp Web

## Antes de enviar
1. Leia o pedido: destinatário (nome e/ou telefone), texto (inline ou caminho de `.txt`), arquivo (caminho). Leia o `.txt` exatamente, sem alterar nada.
2. Confira a permissão (`assessor-zap-core`). Fora dela: pergunte ao dono e espere.
3. Confira os "pare e pergunte" do core: nome no arquivo/texto vs destinatário, arquivo existe e não está vazio.
4. Legenda de arquivo tem limite de 1024 caracteres. Se o texto passar disso, não corte: `falhou: legenda com N caracteres`.

## Envio
1. No WhatsApp Web, abra a conversa: pelo telefone use `https://web.whatsapp.com/send?phone=<só dígitos com DDI>`; pelo nome, busque e confira que há um único resultado exato. Chat "você"/"(você)" = mensagem para si mesmo.
2. Confira o nome/telefone no topo da conversa antes de digitar.
3. **Só texto**: cole no campo de mensagem. Quebra de linha = `Shift+Enter`; `Enter` envia. Prefira colar o texto inteiro de uma vez (colar preserva quebras); nunca aperte `Enter` antes do fim.
4. **Arquivo com legenda**: clipe/"+" → Documento → selecione o arquivo → na prévia, cole o texto no campo de legenda → confira nome do arquivo e legenda → `Enter` ou botão enviar.
5. Um pedido = um envio. Não reenvie se não tiver certeza de que falhou.

## Conferir e reportar
1. Espere a mensagem sair do relógio: ✓ enviado, ✓✓ entregue, ✓✓ azul lido.
2. Responda ao bot que pediu (`SendToAgent`, `priority: true`): `enviado | <destinatário> | <HH:MM> | <tiques>` ou `falhou: <motivo>`.
3. Se enviado sob a permissão, uma linha de log ao dono.

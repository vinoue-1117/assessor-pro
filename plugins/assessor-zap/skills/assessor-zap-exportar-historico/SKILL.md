---
name: assessor-zap-exportar-historico
description: 'Use quando outro bot ou o dono pedir para ler ou exportar mensagens de uma ou mais conversas do WhatsApp para arquivo de texto. Só leitura, nunca envia.'
---

# Exportar histórico (só leitura)

## Regras
- Não digite, não envie, não reaja, não apague, não arquive nada. Se o pedido incluir envio, trate o envio separadamente com `assessor-zap-enviar`.
- Avise quem pediu (uma vez, antes): abrir a conversa marca as mensagens recebidas como lidas e o contato vê os tiques azuis. Se isso não for aceitável, leia só a prévia da lista de conversas (texto cortado) e diga isso no retorno.

## Passos
1. Para cada contato: abra a conversa seguindo "Abrir e fechar conversas" do core (telefone: `https://web.whatsapp.com/send?phone=<dígitos>`; nome: só resultado único com o nome exato). Confira o topo da conversa.
2. Role para cima até ter a quantidade pedida (padrão: últimas 30 mensagens).
   Ao terminar cada contato, feche a conversa (`Esc` ou voltar à lista).
3. Grave no caminho pedido (padrão `/workspace/wo/export/<contato>.txt`), UTF-8, uma linha por mensagem:
   `AAAA-MM-DD HH:MM | eu|contato | texto` (anexo: `[arquivo: <nome>]`; áudio: `[áudio]`).
   Conversa inexistente: grave `SEM CONVERSA`.
4. Responda a quem pediu (`SendToAgent`, `priority: true`): quantos contatos lidos, quais não achados, caminhos dos arquivos.
5. Não guarde conteúdo de conversa na memória.

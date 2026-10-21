---
name: xpp-whatsapp-triagem
description: 'Use na rotina de leitura do WhatsApp (opcional) para ler conversas não lidas, classificar e encaminhar cada uma ao bot certo segundo /workspace/wo/roteamento.md. Silenciosa quando não há nada novo.'
---

# Triagem de mensagens recebidas (opcional)

Só funciona se o dono configurou rotas. Nunca responde ninguém.

## Arquivos
- `/workspace/wo/roteamento.md`: rotas que o dono definiu neste chat, uma por linha: `<contato ou grupo ou assunto> -> <nome do bot> (<id do bot>)`. Sem o arquivo ou sem rotas: termine em silêncio.
- `/workspace/wo/estado.json`: `{"<conversa>": "<id ou data+hora+início do texto da última mensagem encaminhada>"}`. Crie vazio se faltar.
- `/workspace/wo/anexos/`: anexos baixados.

## Passos
1. Abra o WhatsApp Web e filtre "Não lidas". Considere só conversas que casam com alguma rota; as demais não abra (evita tique azul) e não relate.
2. Para cada conversa elegível, leia as mensagens novas depois da marca em `estado.json`. Abrir marca como lido.
3. Classifique contra as rotas. Destino claro: encaminhe ao bot (`SendToAgent`, `priority: true`): contato/grupo, texto exato, anexos (salvos em `anexos/`), horário local e o motivo da classificação em uma linha. Sem destino claro (rota por assunto ambígua): resumo de uma linha para o dono.
4. Atualize `estado.json` após cada encaminhamento, para nunca encaminhar a mesma mensagem duas vezes.
5. Ignore spam, mensagens automáticas e grupos sem menção ao dono.
6. Nada novo: termine sem mensagem nenhuma.
7. Respostas dos bots de destino voltam como pedidos de envio normais (`xpp-whatsapp-enviar`, com a regra de permissão).

## Rotina sugerida
Pausada por padrão; o dono liga. Ex.: a cada 15 min em dias úteis, horário comercial. Cada execução abre o navegador, então custa mais que uma rotina comum.

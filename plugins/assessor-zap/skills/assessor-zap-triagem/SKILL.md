---
name: assessor-zap-triagem
description: 'Use na rotina de leitura do WhatsApp para ler as conversas que têm rota em /workspace/wo/contatos.json e encaminhar cada mensagem nova ao bot dono da rota. Silenciosa quando não há nada novo.'
---

# Triagem: rotas de acompanhamento

Única rotina de leitura do WhatsApp. Só roda enquanto houver rota. Nunca responde ninguém.

## Arquivos
- `/workspace/wo/contatos.json`: contatos, apelidos e `rotas` (formato no `assessor-zap-core`). Sem o arquivo ou com `rotas` vazia: pause esta rotina e termine em silêncio.
- `/workspace/wo/anexos/`: anexos baixados.

## Passos
1. Leia `rotas`. Rota com `expira` vencido: remova do arquivo e avise o `dono_bot_id` (`rota <id> expirou`).
2. Abra o WhatsApp Web e filtre "Não lidas". Considere só conversas cujo contato tem rota; as demais não abra (evita tique azul) e não relate. Abra cada uma seguindo "Abrir e fechar conversas" do core (telefone de `contatos` quando houver) e confira o topo.
3. Leia as mensagens novas depois de `ultima_repassada` daquela rota.
4. Encaminhe ao `dono_bot_id` (`SendToAgent`, `priority: true`): contato, texto exato, anexos (salvos em `anexos/`), horário local e o `id` da rota.
5. Atualize `ultima_repassada` da rota logo após cada encaminhamento, para nunca encaminhar a mesma mensagem duas vezes. Feche a conversa antes de passar à próxima e, ao fim da varredura, deixe a tela na lista de conversas, sem nenhuma aberta.
6. Nada novo: termine sem mensagem nenhuma.
7. Respostas dos bots donos voltam como pedidos de envio normais (`assessor-zap-enviar`; o gate é do bot que pede).

## Rotina
Uma só, deste bot, a cada 5 min (mínimo). Ligada só enquanto `rotas` não estiver vazia: o WO liga ao abrir a primeira rota e pausa quando a última é removida. Pausar ou ligar a rotina nunca para outros trabalhos do WO. Cada execução abre o navegador, então custa mais que uma rotina comum.

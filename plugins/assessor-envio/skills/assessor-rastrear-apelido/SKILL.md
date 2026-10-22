---
name: assessor-rastrear-apelido
description: 'Use quando o assessor pedir para preencher ou corrigir a coluna apelido da planilha de clientes a partir de como ele chama cada cliente no WhatsApp.'
---

# Rastrear apelidos no WhatsApp (via bot de WhatsApp, só leitura)

Descobre como o assessor chama cada cliente (ex.: "Fala, Zé" → `Zé`) e propõe a coluna `apelido`. Nada é enviado; a planilha só muda depois da aprovação.

## Passos
1. Planilha: a última em `/workspace/assessor/clientes.*` (colunas `conta_xp, telefone, nome, apelido`). `conta_xp` é o número da conta na corretora. Escopo: o que o assessor pedir (todos, só os sem apelido, ou contas específicas). Ignore linhas sem telefone (liste-as no fim).
2. `whatsapp_bot_id` da memória (se faltar, setup em `assessor-envio-core`).
3. UMA chamada `SendToAgent` (`priority: true`) para o bot de WhatsApp, com a lista `conta_xp | telefone | nome`:
   ```
   LEITURA APENAS — não envie, não responda, não reaja a nada.
   Para cada contato abaixo, abra a conversa pelo telefone e copie as últimas 30 mensagens (autor: eu/contato, data, texto).
   Grave em /workspace/assessor/conversas/<conta_xp>.txt. Contato sem conversa: grave "SEM CONVERSA".
   Responda quando terminar, com quantos leu e quais não achou.
   ```
   Avise o assessor antes: abrir a conversa marca as mensagens como lidas (tique azul).
4. Para cada `<conta_xp>.txt`, olhe SÓ as mensagens do assessor (autor "eu"). Procure vocativos de saudação: "Oi/Olá/Fala/Bom dia/Boa tarde/E aí, <X>", "<X>, tudo bem?", títulos ("Dr. X", "Dona X"). Apelido = a forma mais frequente, com a grafia usada. Não deduza do nome da planilha nem do nome de perfil do contato.
5. Mostre a proposta em tabela, uma linha por conta:
   `conta_xp | nome | apelido atual | proposto | evidência (trecho + data) | confiança (alta: ≥2 ocorrências / baixa: 1 / sem evidência)`
   Destaque onde o proposto difere do atual. Sem evidência → não propõe (mantém o atual).
6. Pergunte: aprova todos, só os de confiança alta, ou quais contas?
7. Só após a aprovação: grave `/workspace/assessor/clientes.csv` (UTF-8, mesmas 4 colunas) alterando apenas `apelido` das contas aprovadas; guarde a versão anterior como `clientes.bak-<AAAAMMDD-HHMM>.csv`. Mande o arquivo atualizado ao assessor para ele manter a cópia dele.

## Regras
- Este fluxo nunca envia mensagem. Se o bot de WhatsApp perguntar algo sobre envio, a resposta é "não enviar".
- Não altere telefone, nome ou conta. Não guarde trechos de conversa na memória; apague `/workspace/assessor/conversas/` ao final.

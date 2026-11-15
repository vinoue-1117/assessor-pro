# Só o bot de WhatsApp lê o WhatsApp; os outros bots pedem a ele o acompanhamento

Um bot que precisa acompanhar uma conversa pede o acompanhamento ao bot de WhatsApp e nunca cria rotina própria de leitura. O bot de WhatsApp mantém uma única rotina de leitura, ligada só enquanto houver conversa acompanhada, encaminha cada mensagem nova ao bot que pediu e guarda contatos, apelidos confirmados e acompanhamentos num estado único, fora do repositório. Um leitor só evita rotinas duplicadas, uso repetido e conversas marcadas como lidas sem necessidade.

## Alternativas consideradas

Cada bot com a própria rotina de leitura do WhatsApp, e estado espalhado em texto livre e arquivos avulsos: com rotinas assim, a leitura chegou a 48% do uso semanal, e uma parada geral pedida por um bot atingia os outros.

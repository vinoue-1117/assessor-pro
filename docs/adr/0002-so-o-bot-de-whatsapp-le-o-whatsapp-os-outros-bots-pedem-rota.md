# Só o bot de WhatsApp lê o WhatsApp; os outros bots pedem rota a ele

Um bot que precisa acompanhar uma conversa pede uma rota ao bot de WhatsApp e nunca cria rotina própria de leitura. O bot de WhatsApp mantém uma única triagem, ligada só enquanto houver rota, e guarda contatos, apelidos confirmados e rotas num estado único, fora do repositório. Um leitor só evita rotinas duplicadas, consumo de uso repetido e conversas marcadas como lidas sem necessidade.

## Alternativas consideradas

Cada bot com a própria rotina de checagem do WhatsApp, e estado espalhado em texto livre e arquivos avulsos. Era o que existia: a leitura chegou a 48% do uso semanal, e uma parada geral pedida por um bot atingia os outros.

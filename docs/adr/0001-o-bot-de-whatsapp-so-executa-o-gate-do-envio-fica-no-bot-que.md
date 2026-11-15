# O bot de WhatsApp só executa; o gate do envio fica no bot que pede

O envio de relatórios é dividido em dois bots. O bot de relatórios prepara o lote e guarda a aprovação do assessor; o bot de WhatsApp cumpre o pedido de outro bot do dono sem guardar permissão própria nem pedir confirmação, e devolve `falhou` quando uma conferência não passa. Assim a decisão de enviar fica num lugar só, e texto lido em conversa, arquivo ou página nunca vira pedido.

## Alternativas consideradas

Permissão permanente do dono registrada no bot de WhatsApp, com parada para perguntar antes de enviar: a decisão ficaria dividida entre os dois bots.

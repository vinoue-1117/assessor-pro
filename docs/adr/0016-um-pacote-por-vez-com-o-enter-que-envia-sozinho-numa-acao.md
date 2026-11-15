# Um pacote por vez, com o Enter que envia sozinho numa ação

O bot de WhatsApp processa um pacote inteiro antes de começar o seguinte, e o Enter que envia vai sozinho numa ação. No primeiro `falhou` os pacotes seguintes não são tentados e a resposta diz isso, uma linha por pacote, para que quem pediu saiba o que saiu.

## Alternativas consideradas

Juntar o Enter de um pacote com o anexo do seguinte numa ação só, para ganhar tempo: a ação parou a máquina por dois minutos e, interrompida, deixou texto conferido na caixa sem enviar.

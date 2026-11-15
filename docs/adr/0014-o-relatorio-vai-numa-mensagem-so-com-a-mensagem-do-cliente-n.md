# O relatório vai numa mensagem só, com a mensagem do cliente na legenda

O envio ao cliente é uma mensagem única: o relatório com o texto na legenda. Assim um `falhou` significa que nada saiu. O limite de 1.024 caracteres da legenda é conferido no preparo, que bloqueia a conta cuja mensagem não cabe.

## Alternativas consideradas

Relatório e texto em duas mensagens. Era o desenho anterior, sem teto de tamanho, mas deixava o caso de relatório enviado e texto não, e pedia regra de reenvio.

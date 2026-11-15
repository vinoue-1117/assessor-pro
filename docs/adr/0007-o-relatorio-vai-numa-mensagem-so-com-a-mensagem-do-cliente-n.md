# O relatório vai numa mensagem só, com a mensagem do cliente na legenda

O envio ao cliente é uma mensagem única: o relatório XP performance com a mensagem do cliente na legenda. Assim um `falhou` significa que nada saiu. O limite de 1.024 caracteres da legenda é conferido no preparo, que bloqueia a conta cuja mensagem não cabe, e o discurso macro tem teto próprio para caber nele.

## Alternativas consideradas

Relatório e texto em duas mensagens: sem teto de tamanho, mas com o caso de relatório enviado sem o texto, que pede regra de reenvio.

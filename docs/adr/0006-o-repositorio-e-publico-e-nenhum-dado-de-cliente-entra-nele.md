# O repositório é público e nenhum dado de cliente entra nele

O repositório fica público para que os bots baixem skills e scripts sem token. Como o histórico público não se apaga, nome, conta, telefone, valor e posição de carteira nunca entram: arquivo de dado não é versionado, amostra usa valor fictício em tudo que é do cliente, e resultado de rodada de avaliação fica fora do repositório. A recusa de arquivo de dado roda com o script da branch de destino, para que uma PR não consiga desligá-la.

## Alternativas consideradas

Repositório privado com download autenticado por token: exigiria token em cada bot e reinstalação de todos. Rodar a recusa com o script da própria PR: a PR poderia alterar o script e passar.

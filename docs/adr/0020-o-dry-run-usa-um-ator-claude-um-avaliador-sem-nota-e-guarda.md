# O dry run usa um ator Claude, um avaliador sem nota e guarda o resultado fora do repositório

No dry run um Claude faz o papel do bot com as skills da branch, e um avaliador lê o transcript e escreve só o relatório de desvios. Como o ator não é o modelo do bot real, o dry run compara versões de uma skill e não mede o número absoluto do bot. Transcript, relatório e amostras ficam numa pasta de dados privada, porque podem trazer dado de conta e o repositório é público.

## Alternativas consideradas

Rodar tudo no bot real: exige o dono para acionar e exportar e só acontece depois da promoção. Nota ou régua automática: não adotada. Guardar as rodadas no repositório: rejeitado pelo dado que elas podem conter.

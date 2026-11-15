# Script baixado só substitui o de trabalho se o download e a versão conferirem; os ponteiros são a exceção

Cada skill baixa o script da stable para um arquivo temporário e só troca a cópia de trabalho se o download deu certo e a versão é igual ou maior que a versão mínima. Se falhar, a skill para e não usa a cópia do disco, porque uma cópia velha não conhece o subcomando novo. Os ponteiros ainda baixam a skill completa direto por cima da cópia: mudar o corpo do ponteiro obriga a reinstalar todos os bots, e o risco foi considerado baixo.

## Alternativas consideradas

Baixar direto por cima da cópia e conferir só o prefixo da primeira linha: com download falho, a cópia velha seguia em uso sem aviso. Aplicar o arquivo temporário também aos ponteiros: adiado até a primeira reinstalação que outra mudança obrigar.

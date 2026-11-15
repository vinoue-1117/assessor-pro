# O próprio bot se instala, a partir de um prompt colado no chat

O dono cola no chat do bot o prompt de instalação, que diz a função do bot e a pasta dele. O bot lê a ficha e o procedimento de instalação na stable, confere pela função se é ele mesmo, grava o perfil e os ponteiros e devolve uma checklist; o mesmo prompt serve para atualizar. A identidade vale pela função porque o nome do bot no chat varia de conta para conta. O bot pessoal grava os ponteiros na biblioteca de skills do dono, junto com os dos outros bots dele e com as skills pessoais do dono; por isso a instalação só apaga ou sobrescreve skill que aponta para a pasta do próprio bot, e só tira skill órfã com o ok do dono.

## Alternativas consideradas

Um bot de configuração que instalaria os outros: na plataforma cada bot só altera a si mesmo. Limitar a biblioteca de skills do dono aos ponteiros de um só bot deste repositório: deixaria o bot de relatórios e o bot de WhatsApp, que trabalham juntos, fora do plano particular.

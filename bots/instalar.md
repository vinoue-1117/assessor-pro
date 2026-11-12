# Instalar ou atualizar um bot

Instruções para o bot que configura os outros bots do dono. O dono diz qual bot quer pelo caminho da pasta, por exemplo `assessor/envio` ou `assessor/zap`.

Os arquivos vêm sempre da branch `stable`:

`https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/bots/<caminho>/`

## Passos

1. Baixe `bot.md` desse endereço. Se o download falhar ou vier vazio, pare e avise o dono.
2. Nome do bot: o título do `bot.md`.
3. Perfil: o texto da seção `## Perfil`, inteiro e sem alterar.
4. Skills: para cada linha da seção `## Skills`, baixe `ponteiros/<skill>/SKILL.md` e crie no bot uma skill com esse conteúdo, sem alterar. Não instale o arquivo de `skills/`: o ponteiro baixa a skill completa a cada uso, e é assim que o bot recebe as atualizações. Crie as skills no bot, não como skills globais.
5. Rotinas e conexões: faça o que as seções `## Rotinas` e `## Conexões` disserem. Com `Nenhuma`, não crie nada.
6. Confira: o bot tem as skills da lista, cada uma com o conteúdo igual ao do ponteiro baixado. Diga ao dono o que foi criado e o que ele ainda precisa fazer (a seção `## Conexões`).

## Atualizar um bot que já existe

Os mesmos passos. Substitua o perfil e cada ponteiro pelo conteúdo atual. Skill do bot que não está mais na lista: mostre ao dono e remova só se ele confirmar.

Não apague nem altere arquivos do workspace do bot (planilha, histórico de envios, contatos). Eles não fazem parte da instalação.

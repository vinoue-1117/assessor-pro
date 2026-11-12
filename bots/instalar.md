# Instalar ou atualizar este bot

Instruções para o bot que está lendo este arquivo. Você atualiza as suas próprias skills, no seu escopo de bot. O dono cola um prompt no seu chat; esse prompt diz qual bot você é e o caminho da sua pasta (por exemplo `assessor/envio`), e manda seguir este arquivo.

Os arquivos vêm sempre da branch `stable`:

`https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/bots/<caminho>/`

O `bot.md` dessa pasta é a única lista do que você instala: nome, perfil, skills, rotinas e conexões. Este arquivo não repete nada dele.

## Passos

1. Baixe `bot.md` desse endereço. Se o download falhar ou vier vazio, pare e avise o dono.
2. Confira o título do `bot.md` com o bot que o prompt disse que você é. Se for o nome de outro bot, pare e diga que este prompt é para outro bot. Não instale.
3. Perfil: o texto da seção `## Perfil`, inteiro e sem alterar, no seu próprio perfil.
4. Skills: para cada linha da seção `## Skills`, baixe `ponteiros/<skill>/SKILL.md` e grave esse conteúdo, sem alterar, como skill do escopo deste bot. O escopo global e o escopo pessoal não recebem estas skills. Não instale o arquivo de `skills/`: o ponteiro baixa a skill completa a cada uso, e é assim que você recebe as atualizações. Se o download de algum ponteiro falhar ou vier vazio, pare e avise o dono.
5. Onde já existir skill sua com o mesmo nome de um ponteiro da seção `## Skills`, apague essa skill e crie de novo com o ponteiro. Apague só esses nomes.
6. Rotinas e conexões: faça o que as seções `## Rotinas` e `## Conexões` disserem. Com `Nenhuma`, não crie nada.
7. Não apague nada do workspace (planilha, histórico de envios, contatos). Isso não faz parte da instalação.
8. Liste as skills que ficaram, cada uma com a description, e diga ao dono o que ele ainda precisa fazer (a seção `## Conexões`).

## Atualizar

Os mesmos passos. O perfil e cada ponteiro passam a ser o conteúdo atual.

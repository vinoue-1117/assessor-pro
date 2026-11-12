# Instalar ou atualizar este bot

Instruções para o bot que está lendo este arquivo. Você atualiza as suas próprias skills, no seu escopo de bot. O dono cola um prompt no seu chat; esse prompt diz a sua função e o caminho da sua pasta (por exemplo `assessor/envio`), e manda seguir este arquivo.

Os arquivos vêm sempre da branch `stable`:

`https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/bots/<caminho>/`

O `bot.md` dessa pasta é a única lista do que você instala: perfil, skills, rotinas e conexões. Este arquivo não repete nada dele. O título do `bot.md` não precisa bater com o seu nome.

## Passos

1. Baixe `bot.md` desse endereço. Se o download falhar ou vier vazio, pare e avise o dono.
2. Identidade, antes de instalar. Vale a função, nunca o título nem o nome. A função está no prompt e no `bot.md` (o texto de abertura e `## Perfil`); o nome que aparecer nesse texto não precisa ser o seu. Skills que você já tem também confirmam: em `assessor/envio`, prefixo `assessor-envio-*` ou `assessor-*`, e `assessor-zap-*` não é deste caminho; em `assessor/zap`, prefixo `assessor-zap-*`. Se a função ou essas skills forem de outro bot, pare e diga que este prompt é para outro bot. Não instale.
3. Perfil: o texto da seção `## Perfil`, inteiro e sem alterar, no seu próprio perfil.
4. Skills: para cada linha da seção `## Skills`, baixe `ponteiros/<skill>/SKILL.md` e grave esse conteúdo, sem alterar, como skill do escopo deste bot. O escopo global e o escopo pessoal não recebem estas skills. Não instale o arquivo de `skills/`: o ponteiro baixa a skill completa a cada uso, e é assim que você recebe as atualizações. Se o download de algum ponteiro falhar ou vier vazio, pare e avise o dono.
5. Onde já existir skill sua com o mesmo nome de um ponteiro da seção `## Skills`, apague essa skill e crie de novo com o ponteiro. Apague só esses nomes.
6. Skill órfã: skill sua com prefixo `assessor-` que não está mais na seção `## Skills`. Mostre o nome ao dono e só apague com o ok dele. Sem o ok, deixe a skill.
7. Rotinas e conexões: faça o que as seções `## Rotinas` e `## Conexões` disserem. Com `Nenhuma`, não crie nada.
8. Higiene: apague só as cópias baixadas pelos ponteiros, os arquivos `/workspace/assessor-pro/*.md`. O ponteiro grava cada skill nesse caminho (`/workspace/assessor-pro/<skill>.md`). Ponteiro antigo, que baixava de `plugins/**`, gravava o mesmo arquivo. Liste cada um que apagar; se não houver, diga que não havia. Não toque em planilha, histórico de envios, contatos nem em qualquer outro arquivo.
9. Teste rápido: carregue pelo ponteiro a skill core que o `## Perfil` manda seguir e confirme que o download e a conferência do frontmatter funcionam. Se falhar, pare e avise o dono.
10. Devolva a checklist abaixo marcada. Se ficou skill órfã, diga os nomes junto.

## Checklist

Marque cada item. No 3, troque cada N: ponteiros gravados e linhas da seção `## Skills`. No 4, liste os arquivos (ou diga que não havia).

- [ ] 1. Identidade conferida
- [ ] 2. Perfil atualizado
- [ ] 3. N de N ponteiros gravados
- [ ] 4. Cópias velhas limpas (lista)
- [ ] 5. Workspace preservado
- [ ] 6. Teste rápido: carregar a skill core pelo ponteiro e confirmar que o download e a conferência do frontmatter funcionam
- [ ] 7. O que falta o dono fazer (`## Conexões`)

## Atualizar

Os mesmos passos. O perfil e cada ponteiro passam a ser o conteúdo atual.

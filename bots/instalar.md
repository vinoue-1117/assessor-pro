# Instalar ou atualizar este bot

Instruções para o bot que está lendo este arquivo. O dono cola um prompt no seu chat; esse prompt diz a sua função e o caminho da sua pasta (por exemplo `assessor/envio`), e manda seguir este arquivo. O objetivo é deixar gravados o seu perfil e os ponteiros das suas skills, prontos para a próxima conversa.

Os arquivos vêm sempre da branch `stable`:

`https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/bots/<caminho>/`

O `bot.md` dessa pasta é a única lista do que você instala: perfil, skills, rotinas e conexões. Este arquivo não repete nada dele. O título do `bot.md` não precisa bater com o seu nome.

## Onde gravar

Bot de time guarda skills próprias, que só ele vê. Bot do plano particular não guarda: a plataforma recusa skill própria, e as skills dele ficam na biblioteca de skills do dono, que todos os bots pessoais do dono veem. Grave os ponteiros nas suas skills próprias, todos no mesmo lugar. Só a recusa de skill própria leva à biblioteca do dono. Outra recusa: pare e avise o dono. O escopo global nunca recebe estes ponteiros.

Descubra o lugar antes de mudar o perfil: pelo seu catálogo de skills, se ele mostra onde você guarda skill, ou gravando o primeiro ponteiro da `## Skills` nas skills próprias. A recusa dessa gravação já diz que o lugar é a biblioteca do dono.

## Suas skills e as dos outros

Skill sua deste repositório é a que aponta para `bots/<caminho>/skills/<nome>/SKILL.md`, com o `<caminho>` do prompt. Na biblioteca do dono aparecem também ponteiros de outros bots deste repositório (outro `<caminho>`) e as skills pessoais do dono. Nenhuma delas é sua.

Três limites protegem o que não é seu:

- Não apague nem sobrescreva skill que não aponta para a sua pasta, mesmo que tenha o nome de uma linha da `## Skills`: skill pessoal do dono com esse nome é dele. A exceção é o ponteiro antigo, descrito abaixo. A conferência dos nomes é o passo 3.
- Skill órfã é a que aponta para a sua pasta com um `<nome>` fora da `## Skills`. Mostre o nome ao dono e só apague com o ok dele. Sem o ok, deixe a skill.
- Cada ponteiro fica gravado como skill. Ponteiro lido e guardado só na memória da conversa não existe na próxima.

O nome de cada skill é único no repositório. Por isso, skill com a marca do repositório (`raw.githubusercontent.com/vinoue-1117/assessor-pro` no texto) e nome da `## Skills` é ponteiro seu, mesmo a antiga que aponta para `plugins/`, e dá lugar ao ponteiro atual, nas skills próprias e na biblioteca do dono. Para a órfã, nas skills próprias de um bot de time, toda skill com a marca e nome fora da `## Skills` é órfã; na biblioteca do dono, só a que aponta para a sua pasta.

## Passos

1. Baixe `bot.md` do endereço acima. Se o download falhar ou vier vazio, pare e avise o dono.
2. Identidade, antes de instalar. Vale a função, nunca o título nem o nome. A função está no prompt e no `bot.md` (o texto de abertura e `## Perfil`); o nome que aparecer nesse texto não precisa ser o seu. Se você guarda skills próprias deste repositório (com `raw.githubusercontent.com/vinoue-1117/assessor-pro` no texto), elas também confirmam: alguma tem nome da `## Skills`. Na biblioteca do dono essa conferência não vale, porque ela tem os ponteiros dos outros bots dele. Se a função for de outro bot, ou se as suas skills próprias deste repositório não têm nenhum nome da `## Skills`, pare e diga que este prompt é para outro bot. Não instale.
3. Lugar e nomes, antes de mudar o perfil: descubra onde vai gravar (seção `## Onde gravar`). Nesse lugar, para cada linha da `## Skills`, veja se já existe skill com esse nome. Se alguma existe e não é sua (seção acima), não mude o perfil nem grave mais ponteiros: mostre o nome ao dono e pare.
4. Perfil: o texto da seção `## Perfil`, inteiro e sem alterar, no seu próprio perfil.
5. Skills: para cada linha da seção `## Skills`, baixe `ponteiros/<skill>/SKILL.md` e grave esse conteúdo, sem alterar, como skill. Ponteiro seu que já existe com o mesmo nome dá lugar ao conteúdo atual. Não instale o arquivo de `skills/`: o ponteiro baixa a skill completa a cada uso, e é assim que você recebe as atualizações. Se o download de algum ponteiro falhar ou vier vazio, pare e avise o dono.
6. Órfãs: no lugar onde gravou, procure skill órfã (seção acima). Mostre os nomes ao dono e só apague com o ok dele. Sem o ok, deixe a skill.
7. Rotinas e conexões: faça o que as seções `## Rotinas` e `## Conexões` disserem. Com `Nenhuma`, não crie nada.
8. Higiene: apague só as cópias baixadas pelos seus ponteiros, `/workspace/assessor-pro/<skill>.md` para cada nome da `## Skills`. O `/workspace` pode ser dividido com outros bots do dono, e cópia de outro nome é deles: não apague. Ponteiro antigo, que baixava de `plugins/**`, gravava o mesmo arquivo. Liste cada um que apagar; se não houver, diga que não havia. Não toque em planilha, histórico de envios, contatos nem em qualquer outro arquivo.
9. Teste rápido: carregue pelo ponteiro a skill core que o `## Perfil` manda seguir e confirme que o download e a conferência do frontmatter funcionam. Se falhar, pare e avise o dono.
10. Devolva a checklist abaixo marcada. Se ficou skill órfã, diga os nomes junto.

## Checklist

Marque cada item. No 3, troque cada N (ponteiros gravados e linhas da seção `## Skills`) e diga onde gravou: skills próprias do bot ou biblioteca do dono. No 4, liste os arquivos (ou diga que não havia).

- [ ] 1. Identidade conferida
- [ ] 2. Perfil atualizado
- [ ] 3. N de N ponteiros gravados em (skills próprias do bot ou biblioteca do dono)
- [ ] 4. Cópias velhas limpas (lista)
- [ ] 5. Workspace preservado
- [ ] 6. Teste rápido: carregar a skill core pelo ponteiro e confirmar que o download e a conferência do frontmatter funcionam
- [ ] 7. O que falta o dono fazer (`## Conexões`)

## Atualizar

Os mesmos passos. O perfil e cada ponteiro passam a ser o conteúdo atual.

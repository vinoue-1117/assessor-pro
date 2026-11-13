# Instalar ou atualizar este bot

Instruções para o bot que está lendo este arquivo. Você atualiza as suas próprias skills. O dono cola um prompt no seu chat; esse prompt diz a sua função e o caminho da sua pasta (por exemplo `assessor/envio`), e manda seguir este arquivo.

O ponteiro fica num escopo só, o que a plataforma aceitar neste bot:

- Bot de time, compartilhado, guarda skill no escopo `bot`. Grave com `scope: "bot"`. Não grave estes ponteiros na biblioteca pessoal do dono, e não apague o que já estiver lá: pode ser de outro bot pessoal do mesmo dono.
- Bot pessoal, sem time, não guarda skill própria. A plataforma recusa o `scope: "bot"` com `cannot keep skills of its own` e manda gravar sem `scope` na biblioteca de skills do dono. Grave sem `scope`, ou com `scope: "user"` se a ferramenta exigir o campo: é a mesma biblioteca, compartilhada por todos os bots pessoais desse dono. Não deixe o ponteiro só na memória.

O escopo global não recebe estes ponteiros. Qualquer outra recusa para o processo: não passe para `user` por outro motivo.

Os arquivos vêm sempre da branch `stable`:

`https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/bots/<caminho>/`

O `bot.md` dessa pasta é a única lista do que você instala: perfil, skills, rotinas e conexões. Este arquivo não repete nada dele. O título do `bot.md` não precisa bater com o seu nome.

Skill deste repositório tem `raw.githubusercontent.com/vinoue-1117/assessor-pro` no texto. Ponteiro deste bot é a skill cujo texto tem a URL `bots/<caminho>/skills/<nome>/SKILL.md`, com o `<caminho>` do prompt e a barra depois dele. O `<nome>` é o trecho entre `skills/` e `/SKILL.md`. URL de script (`/scripts/`) não é ponteiro. Não reconheça skill pelo prefixo do nome.

## Passos

1. Baixe `bot.md` desse endereço. Se o download falhar ou vier vazio, pare e avise o dono.
2. Identidade, antes de instalar. Vale a função, nunca o título nem o nome. A função está no prompt e no `bot.md` (o texto de abertura e `## Perfil`); o nome que aparecer nesse texto não precisa ser o seu. Compare com o seu perfil atual. Perfil vazio não é outra função. Se o perfil atual descreve outra função, pare e diga que este prompt é para outro bot. Não instale.

   A confirmação por nome de skill olha só o escopo `bot`. Se nesse escopo alguma skill deste repositório tem nome da seção `## Skills`, este `bot.md` é o seu. Se nesse escopo há skill deste repositório e nenhuma tem nome da seção `## Skills`, pare e diga que este prompt é para outro bot. Não instale.

   A biblioteca pessoal fica de fora dessa conta. Sem skill no escopo `bot`, a decisão é a função. Skill dessa biblioteca com nome fora da seção `## Skills` é outro bot do mesmo dono, ou skill pessoal dele: não é motivo para parar. Nome que está na seção também não prova que este chat é o bot deste `bot.md`, porque a biblioteca é compartilhada.
3. Perfil: o texto da seção `## Perfil`, inteiro e sem alterar, no seu próprio perfil.
4. Skills: para cada linha da seção `## Skills`, baixe `ponteiros/<skill>/SKILL.md` e grave esse conteúdo, sem alterar. Não instale o arquivo de `skills/`: o ponteiro baixa a skill completa a cada uso, e é assim que você recebe as atualizações. Se o download de algum ponteiro falhar ou vier vazio, pare e avise o dono.

   O escopo é um só, decidido no primeiro ponteiro e repetido nos outros. Grave o primeiro com `scope: "bot"`. Se gravar, os outros também. Não grave estes ponteiros na biblioteca pessoal, e não apague lá skill nenhuma. Se a plataforma recusar com `cannot keep skills of its own`, o escopo é `user`: grave esse ponteiro e os outros sem `scope` (ou com `scope: "user"`). Não tente `bot` de novo. No escopo `user`, o passo 5 vem antes de cada gravação. Qualquer outra recusa: pare e avise o dono, sem gravar em `user`.
5. Ao gravar um nome que já existe no mesmo escopo, substitua pelo ponteiro. Apague só esses nomes, e só nesse escopo.

   No escopo `bot`, apague a de mesmo nome e grave o ponteiro, com ou sem a marca do repositório. Não apague nada na biblioteca pessoal.

   No escopo `user`, apague a de mesmo nome só quando o texto tiver a marca do repositório. O nome é único no repositório, então essa é o ponteiro que você está atualizando. Sem a marca, é skill pessoal do dono: não apague, não grave por cima, pare e avise o nome.
6. Skill órfã, só no escopo em que você gravou, depois de gravar os ponteiros. Mostre o nome ao dono e só apague com o ok dele. Sem o ok, deixe a skill. Leia o texto da skill antes de decidir.

   No escopo `bot`: skill sua desse escopo, com a marca deste repositório, cujo nome não está na seção `## Skills`. Não olhe a biblioteca pessoal.

   No escopo `user`: skill da biblioteca pessoal cujo texto tem a URL de ponteiro `bots/<caminho>/skills/<nome>/SKILL.md` e esse `<nome>` não está na seção `## Skills`. Fica de fora, sem listar e sem apagar: ponteiro cujo caminho depois de `bots/` é outro, skill sem a marca do repositório, e texto que só cita `/scripts/`.
7. Rotinas e conexões: faça o que as seções `## Rotinas` e `## Conexões` disserem. Com `Nenhuma`, não crie nada.
8. Higiene: apague só as cópias baixadas pelos ponteiros, os arquivos `/workspace/assessor-pro/*.md`. O ponteiro grava cada skill nesse caminho (`/workspace/assessor-pro/<skill>.md`). Ponteiro antigo, que baixava de `plugins/**`, gravava o mesmo arquivo. Liste cada um que apagar; se não houver, diga que não havia. Não toque em planilha, histórico de envios, contatos nem em qualquer outro arquivo.
9. Teste rápido: carregue pelo ponteiro a skill core que o `## Perfil` manda seguir e confirme que o download e a conferência do frontmatter funcionam. Se falhar, pare e avise o dono.
10. Devolva a checklist abaixo marcada, com o escopo em que gravou. Se ficou skill órfã, diga os nomes junto.

## Checklist

Marque cada item. No 3, troque cada N (ponteiros gravados e linhas da seção `## Skills`) e troque `<escopo>` por `bot` ou `user`, o que a plataforma aceitou. No 4, liste os arquivos (ou diga que não havia).

- [ ] 1. Identidade conferida
- [ ] 2. Perfil atualizado
- [ ] 3. N de N ponteiros gravados no escopo <escopo>
- [ ] 4. Cópias velhas limpas (lista)
- [ ] 5. Workspace preservado
- [ ] 6. Teste rápido: carregar a skill core pelo ponteiro e confirmar que o download e a conferência do frontmatter funcionam
- [ ] 7. O que falta o dono fazer (`## Conexões`)

## Atualizar

Os mesmos passos. O perfil e cada ponteiro passam a ser o conteúdo atual. O escopo continua o que a plataforma aceitar neste bot.

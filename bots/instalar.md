# Instalar ou atualizar este bot

Instruções para o bot que está lendo este arquivo. Você atualiza as suas próprias skills. O dono cola um prompt no seu chat; esse prompt diz a sua função e o caminho da sua pasta (por exemplo `assessor/envio`), e manda seguir este arquivo.

O ponteiro fica num escopo só:

- Bot de time grava com `scope: "bot"`. Não grave estes ponteiros na biblioteca pessoal do dono e não apague o que já estiver lá.
- Bot pessoal não guarda skill própria. A plataforma recusa o `scope: "bot"` com `cannot keep skills of its own` e manda gravar sem `scope` na biblioteca de skills do dono, que ela descreve como compartilhada por todos os bots dele. Grave sem `scope`, ou com `scope: "user"` se a ferramenta exigir o campo. Não deixe o ponteiro só na memória.

Nessa biblioteca cabe um caminho só deste repositório. Ponteiro de outro `bots/<caminho>/` já visível: pare antes de gravar e antes de mudar o perfil. A skill core pede para ser seguida em toda conversa, e dois bots pessoais nesta biblioteca não foram testados. Mais de um bot usa bot de time, no escopo `bot`. Não apague o ponteiro do outro caminho.

O escopo global não recebe estes ponteiros. Recusa diferente de `cannot keep skills of its own` no primeiro ponteiro encerra a instalação: não passe para `user`.

Parar encerra a instalação. Não é pular um nome. Se já gravou ponteiro nesta rodada, diga quais. Não apague o que gravou para desfazer.

Os arquivos vêm sempre da branch `stable`:

`https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/bots/<caminho>/`

O `bot.md` dessa pasta é a única lista do que você instala: perfil, skills, rotinas e conexões. Este arquivo não repete nada dele. O título do `bot.md` não precisa bater com o seu nome.

Skill deste repositório tem `raw.githubusercontent.com/vinoue-1117/assessor-pro` no texto. Ponteiro é a skill cujo texto tem a URL `bots/<caminho-da-url>/skills/<nome>/SKILL.md`. O caminho da URL é o trecho entre `bots/` e `/skills/`. O `<nome>` é o trecho entre `skills/` e `/SKILL.md`. URL de script (`/scripts/`) não é ponteiro. Não reconheça skill pelo prefixo do nome. Ponteiro deste bot é aquele em que o caminho da URL é o `<caminho>` do prompt, com a barra que fecha o caminho.

## Passos

1. Baixe `bot.md` desse endereço. Se o download falhar ou vier vazio, pare e avise o dono.
2. Identidade, antes de instalar. Vale a função, nunca o título nem o nome. A função está no prompt e no `bot.md` (o texto de abertura e `## Perfil`); o nome que aparecer nesse texto não precisa ser o seu. Compare com o seu perfil atual. Perfil vazio não é outra função. Se o perfil atual descreve outra função, pare e diga que este prompt é para outro bot.

   A confirmação por nome de skill olha só o escopo `bot`. Se nesse escopo alguma skill deste repositório tem nome da seção `## Skills`, este `bot.md` é o seu. Se nesse escopo há skill deste repositório e nenhuma tem nome da seção `## Skills`, pare e diga que este prompt é para outro bot.

   Nome na biblioteca pessoal não entra nessa conta. Não prova que este chat é o bot deste `bot.md`, e não prova que o prompt é de outro bot.
3. Escopo, no primeiro ponteiro, antes do perfil. Baixe `ponteiros/<skill>/SKILL.md` da primeira linha da seção `## Skills`. Se o download falhar ou vier vazio, pare e avise o dono. Grave com `scope: "bot"`.

   Gravou: o escopo de todos os ponteiros é `bot`. Não grave estes ponteiros na biblioteca pessoal e não apague nada lá. Se um ponteiro seguinte for recusado com `cannot keep skills of its own`, pare. Não grave o resto em `user`. Diga quais ponteiros ficaram no escopo `bot`.

   Recusou este primeiro com `cannot keep skills of its own`: nada foi gravado. Faça o passo 4 antes do perfil e antes de qualquer gravação.

   Outra recusa: pare, sem gravar em `user`.
4. Só quando o primeiro ponteiro foi recusado com `cannot keep skills of its own`. Leia as skills visíveis na biblioteca do dono.

   Outro caminho: há ponteiro (a URL definida acima) cujo caminho entre `bots/` e `/skills/` não é o `<caminho>` deste prompt. Pare. Não grave e não apague. Diga ao dono que a plataforma descreve essa biblioteca como compartilhada por todos os bots dele, que a skill core pede para ser seguida em toda conversa, e que dois bots pessoais nela não foram testados. Mais de um bot deste repositório pede bot de time, com `scope: "bot"`.

   Colisão, em todos os nomes da seção `## Skills`, antes de gravar o primeiro: se já existe skill com um desses nomes e o texto não tem a marca do repositório, pare. Não grave nenhum ponteiro e não grave por cima. Liste os nomes. Nome com a marca é ponteiro deste repositório (o nome é único no repositório) e entra no passo 6.

   Sem outro caminho e sem colisão: o escopo é `user`.
5. Perfil: o texto da seção `## Perfil`, inteiro e sem alterar, no seu próprio perfil. Só depois que o passo 3 fixou o escopo `bot`, ou o passo 4 autorizou `user`.
6. Skills: para cada linha da seção `## Skills`, baixe `ponteiros/<skill>/SKILL.md` e grave esse conteúdo, sem alterar, no escopo já escolhido. O primeiro ponteiro do escopo `bot` já foi gravado no passo 3. Não instale o arquivo de `skills/`: o ponteiro baixa a skill completa a cada uso, e é assim que você recebe as atualizações. Se o download de algum ponteiro falhar ou vier vazio, pare e avise o dono, dizendo quais ponteiros já foram gravados.

   Onde já existir, nesse escopo, skill com o mesmo nome de um ponteiro da seção `## Skills`, apague essa skill e grave o ponteiro. Apague só esses nomes, e só nesse escopo. No escopo `bot`, a de mesmo nome é sua, com ou sem a marca. No escopo `user`, apague a de mesmo nome só quando o texto tiver a marca; sem a marca, o passo 4 já encerrou.
7. Skill órfã, só no escopo em que você gravou, depois de gravar os ponteiros. Mostre o nome ao dono e só apague com o ok dele. Sem o ok, deixe a skill. Leia o texto da skill antes de decidir.

   No escopo `bot`: skill sua desse escopo, com a marca deste repositório, cujo nome não está na seção `## Skills`. Não olhe a biblioteca pessoal.

   No escopo `user`: ponteiro deste bot (caminho da URL igual ao `<caminho>` do prompt) cujo `<nome>` não está na seção `## Skills`. Fica de fora, sem listar e sem apagar: ponteiro de outro caminho, skill sem a marca do repositório, e texto que só cita `/scripts/`.
8. Rotinas e conexões: faça o que as seções `## Rotinas` e `## Conexões` disserem. Com `Nenhuma`, não crie nada.
9. Higiene: apague só as cópias baixadas pelos ponteiros, os arquivos `/workspace/assessor-pro/*.md`. O ponteiro grava cada skill nesse caminho (`/workspace/assessor-pro/<skill>.md`). Ponteiro antigo, que baixava de `plugins/**`, gravava o mesmo arquivo. Liste cada um que apagar; se não houver, diga que não havia. Não toque em planilha, histórico de envios, contatos nem em qualquer outro arquivo.
10. Teste rápido: carregue pelo ponteiro a skill core que o `## Perfil` manda seguir e confirme que o download e a conferência do frontmatter funcionam. Se falhar, pare e avise o dono.
11. Devolva a checklist abaixo marcada, com o escopo em que gravou. Se ficou skill órfã, diga os nomes junto. Se parou antes, não marque o que não fez: diga o passo e o motivo.

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

Os mesmos passos. O perfil e cada ponteiro passam a ser o conteúdo atual. O escopo continua o que a plataforma aceitar neste bot. No escopo `user`, atualizar o mesmo `<caminho>` segue; outro `<caminho>` já presente na biblioteca encerra, como no passo 4.

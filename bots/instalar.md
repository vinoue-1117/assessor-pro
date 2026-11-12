# Instalar ou atualizar este bot

Instruções para o bot que está lendo este arquivo. Você atualiza as suas próprias skills, no seu escopo de bot. O dono cola um prompt no seu chat; esse prompt diz o caminho da sua pasta (`assessor/envio` ou `assessor/zap`) e manda seguir este arquivo.

Os arquivos vêm sempre da branch `stable`:

`https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/bots/<caminho>/`

## Skills esperadas

O `bot.md` baixado tem que bater com esta lista: o título e os nomes, sem sobrar e sem faltar. Se não bater, pare e avise o dono. Não instale.

`assessor/envio`, título `Relatórios - Assessor Pro`:

- `assessor-ajustar-cliente`
- `assessor-enviar-relatorio`
- `assessor-envio-core`
- `assessor-envio-teste`
- `assessor-preparar-envio`
- `assessor-rastrear-apelido`
- `assessor-resumo-ultimo-envio`

`assessor/zap`, título `Whatsapp - Assessor Pro`:

- `assessor-zap-core`
- `assessor-zap-enviar`
- `assessor-zap-exportar-historico`
- `assessor-zap-triagem`

## Passos

1. Baixe `bot.md` desse endereço. Se o download falhar ou vier vazio, pare e avise o dono.
2. Confira o título e os nomes da seção `## Skills` com a lista acima. Se o título não for o deste caminho, pare e diga que este prompt é para outro bot.
3. Perfil: o texto da seção `## Perfil`, inteiro e sem alterar, no seu próprio perfil.
4. Skills: para cada linha da seção `## Skills`, baixe `ponteiros/<skill>/SKILL.md` e grave esse conteúdo, sem alterar, como skill do escopo deste bot. O escopo global e o escopo pessoal não recebem estas skills. Não instale o arquivo de `skills/`: o ponteiro baixa a skill completa a cada uso, e é assim que você recebe as atualizações.
5. Onde já existir skill sua com o mesmo nome de um ponteiro desta lista, apague essa skill e crie de novo com o ponteiro. Apague só esses nomes.
6. Rotinas e conexões: faça o que as seções `## Rotinas` e `## Conexões` disserem. Com `Nenhuma`, não crie nada.
7. Não apague nada do workspace (planilha, histórico de envios, contatos). Isso não faz parte da instalação.
8. Liste as skills que ficaram, cada uma com a description, e diga ao dono o que ele ainda precisa fazer (a seção `## Conexões`).

## Atualizar

Os mesmos passos. O perfil e cada ponteiro passam a ser o conteúdo atual.

## Prompts para o dono

O dono cola um prompt no chat de cada bot. Se você é o bot, não encaminhe estes prompts e não siga os dois: siga só os passos acima, no caminho que o prompt já colado citou.

No chat do bot Relatórios - Assessor Pro:

```
você é o bot de Relatórios do Assessor Pro; se não for, pare e diga que este prompt é para outro bot. Atualize suas skills seguindo https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/bots/instalar.md para o bot assessor/envio. Não apague nada do workspace.
```

No chat do bot Whatsapp - Assessor Pro:

```
você é o bot de WhatsApp do Assessor Pro; se não for, pare e diga que este prompt é para outro bot. Atualize suas skills seguindo https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/bots/instalar.md para o bot assessor/zap. Não apague nada do workspace.
```

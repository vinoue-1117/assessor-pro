# Grok Bot

Como a plataforma em que os bots rodam guarda skills e atualiza bots. É o que o [`bots/instalar.md`](../bots/instalar.md) supõe.

## Onde ficam as skills

| Pasta | Quem acessa |
| --- | --- |
| Pasta própria do bot | Só o bot dono dela |
| Pasta `user` (a biblioteca de skills do dono) | Todo bot, que pode ler e alterar |

| Bot | Skill própria | Atualização quando a origem muda |
| --- | --- | --- |
| Pessoal (plano particular) | Não carrega: as skills dele ficam na pasta `user` | Não se atualiza. Bot criado de template compartilhado é uma cópia do momento da criação |
| De time | Carrega, na pasta própria | Se atualiza. As pastas de arquivos e o histórico de chats não são compartilhados |

Como o bot pessoal não acompanha a origem, as skills chegam a ele pelos [ponteiros](../bots/README.md#ponteiro), que baixam da branch `stable` a cada uso.

## Bot construtor

O bot construtor ([`dr-eggbot-v2`](https://x.ai/bot/marketplace/bots/dr-eggbot-v2)) cria os outros bots. Usar o construtor é opcional e serve para bot pessoal. Ele não acessa a pasta própria de outro bot: o bot de time é instalado com o prompt de instalação colado no chat dele.

Instalação de bot pessoal pelo construtor:

1. O dono pede os bots no chat do construtor, por exemplo: "Leia o repo `https://github.com/vinoue-1117/assessor-pro` e instale os bots relatório/whatsapp".
2. O construtor cria cada bot.
3. O construtor pede a checklist do `instalar.md` e corrige o que faltar.

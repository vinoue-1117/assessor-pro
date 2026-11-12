# Bots

Cada bot do Grok Bot mantido neste repositório tem uma pasta aqui. Os computadores dos bots leem a branch `stable`. A `main` só chega neles quando o dono do repositório promove.

## Pasta de um bot

Bot é toda pasta que tem `bot.md`. Bots do mesmo produto ficam juntos (`assessor/envio`, `assessor/zap`); bot sozinho fica direto em `bots/<bot>/`.

| Caminho | Conteúdo |
| --- | --- |
| `bot.md` | A ficha do bot: perfil, skills, rotinas e conexões. É o que o [`instalar.md`](instalar.md) lê |
| `skills/<skill>/SKILL.md` | A skill completa. Script que só ela usa fica em `skills/<skill>/scripts/` |
| `ponteiros/<skill>/SKILL.md` | Gerado por `python scripts/gerar-ponteiros.py`. Não editar à mão |
| `README.md` | O prompt de instalação, na seção `## Instalar`. Para quem mantém o bot, o que as skills e os scripts fazem |
| `tests/` | Testes em pytest, na pasta do bot ou na do produto. Um arquivo de teste não importa outro: o `check` roda o pytest com `--import-mode=importlib` |

O que mais for só do bot fica na pasta dele: template de página, script de apoio, exemplo de saída.

## bot.md

O título é o nome do bot. As quatro seções existem sempre, com `Nenhuma.` quando não houver o que listar.

- `## Perfil`: o texto do perfil do bot, copiado sem alteração na instalação. Mantenha curto e mande seguir a skill `<bot>-core`: a persona e as regras ficam nela, e assim chegam ao bot por download, sem reinstalar.
- `## Skills`: uma linha por skill, no formato ``- `nome-da-skill`: quando usar``. A frase vira a description do ponteiro. A lista tem que bater com as pastas de `skills/`; o gerador para se sobrar ou faltar.
- `## Rotinas`: cada rotina com horário e o que ela executa.
- `## Conexões`: o que o dono precisa conectar.

O nome de cada skill é único no repositório. Comece pelo nome do bot ou do produto (`assessor-zap-enviar`).

## Ponteiro

O bot instalado não guarda a skill completa. Ele guarda o ponteiro, que baixa a skill completa da `stable` a cada uso. Por isso uma correção promovida chega a todos os bots sem reinstalar. O que fica gravado no bot é o perfil e a lista de ponteiros: mudar um dos dois pede colar de novo o prompt desse bot no chat dele. O bot segue o [`instalar.md`](instalar.md) e se ajusta.

## Prompt de instalação

Fica no `README.md` da pasta do bot, na seção `## Instalar`, e em nenhum outro arquivo. O dono cola no chat do bot para instalar ou atualizar. Formato:

```
você é o bot <quem>; se não for, pare e diga que este prompt é para outro bot. Atualize suas skills seguindo https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/bots/instalar.md para o bot <caminho>. Não apague nada do workspace.
```

`<caminho>` é a pasta do bot dentro de `bots/`. O gerador para se o README do bot não tiver o prompt com esse caminho.

## O que não entra

O repositório é público e o histórico não se apaga.

- Nenhum bot deste repo precisa de chave de API ou token.
- Dado de cliente: nome, conta, telefone, e-mail, valor, posição de carteira. PDF, planilha, CSV e zip não são versionados, e o `check` recusa esses formatos.
- Nome, telefone ou e-mail de terceiro.
- Amostra para teste usa valor fictício em tudo que é do cliente. De real, só o layout das linhas e o que é igual para todos.

## Antes de abrir PR

`python scripts/check.py`

O mesmo comando roda em toda PR. Ele recusa arquivo de dado versionado, confere os ponteiros contra as skills e roda os testes. A recusa de arquivo de dado roda também num segundo workflow (`dados.yml`), com o `check.py` da branch de destino sobre a lista de arquivos da PR: mexer no `check.py` na mesma PR não a desliga. Ele não lê o texto dos arquivos atrás de dado de cliente: essa conferência é de quem abre e de quem revisa a PR.

Uma PR mexe na pasta de um bot. Mudança em `scripts/` ou neste arquivo vai em PR separada.

## Publicar

A edição entra na `main` por PR. Quem promove é o dono do repositório:

`git push origin main:stable`

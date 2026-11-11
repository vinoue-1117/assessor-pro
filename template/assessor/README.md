# Template do bot assessor

O assessor importa os bots por link, sem o Cursor. Cada skill em `template/assessor/skills/` é um ponteiro: na execução ela baixa a skill completa da branch `stable` (primeiro em `bots/assessor/`, depois no caminho antigo em `plugins/`). O perfil do bot é um arquivo em `template/assessor/perfis/`.

`template/` é o getting-started do bot. Um template de página, se existir, fica em `templates-page/` dentro da pasta do bot.

## Publicar

1. Edite na `main` e teste.
2. Se mudou o `name` de uma skill, criou uma skill nova ou mudou o comando de download, rode `python3 tools/gerar-ponteiros.py`. A description do ponteiro não vem da skill completa: é uma frase fixa no mapa `DESCRICOES` de `tools/gerar-ponteiros.py` e só diz quando usar a skill. Mudar a description da skill completa não altera o ponteiro. Skill nova sem entrada no `DESCRICOES` faz o script parar.
3. Promova o que foi testado:

`git push origin main:stable`

Os bots leem sempre `stable`. A `main` não chega neles até essa promoção.

Antes de o repositório ficar privado, cada bot precisa da variável `GITHUB_TOKEN_BOTS` (token de leitura). O valor não entra no repositório. A ordem está no README da raiz.

Só o dono do repositório deve ter escrita aqui.

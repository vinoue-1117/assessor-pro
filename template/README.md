# Template dos bots

O assessor importa os bots por link, sem o Cursor. Cada skill em `template/skills/` é um ponteiro: na execução ela baixa a skill completa da branch `stable`. O perfil do bot é um arquivo em `template/perfis/`.

## Publicar

1. Edite na `main` e teste.
2. Se mudou o `name` ou a `description` de uma skill, rode `python3 scripts/gerar-ponteiros.py`.
3. Promova o que foi testado:

`git push origin main:stable`

Os bots leem sempre `stable`. A `main` não chega neles até essa promoção.

Só Victor Inoue deve ter escrita neste repositório.

# Template dos bots

O assessor importa os bots por link, sem o Cursor. Cada skill em `template/skills/` é um ponteiro: na execução ela baixa a skill completa da branch `stable`. O perfil do bot é um arquivo em `template/perfis/`.

## Publicar

1. Edite na `main` e teste.
2. Se mudou o `name` de uma skill ou criou uma skill nova, rode `python3 scripts/gerar-ponteiros.py`. A description do ponteiro não vem da skill completa: é uma frase fixa no mapa `DESCRICOES` de `scripts/gerar-ponteiros.py` e só diz quando usar a skill. Mudar a description da skill completa não altera o ponteiro. Skill nova sem entrada no `DESCRICOES` faz o script parar.
3. Promova o que foi testado:

`git push origin main:stable`

Os bots leem sempre `stable`. A `main` não chega neles até essa promoção.

4. Se o `gerar-ponteiros.py` mudou o corpo dos ponteiros (o texto ou o comando de download, não só a lista de skills), reimporte as skills em cada bot depois da promoção. O ponteiro instalado não muda com a promoção: só a skill completa que ele baixa muda.

Só Victor Inoue deve ter escrita neste repositório.

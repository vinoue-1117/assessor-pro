# Domain docs

Como as skills de engenharia consomem a documentação de domínio deste repo ao explorar o código.

## Antes de explorar, ler

- **`GLOSSARY.md`** na raiz do repo.
- **`docs/adr/`**: os ADRs que tocam a área em que o trabalho vai mexer.

Se algum desses arquivos não existir, **seguir sem avisar**. Não apontar a ausência nem sugerir criar de antemão. A skill `/domain-modeling` (alcançada pela `/grill-with-docs` e pela `/improve-codebase-architecture`) cria os arquivos quando um termo ou uma decisão é de fato resolvido.

## Estrutura de arquivos

O repo é single-context:

```
/
├── GLOSSARY.md
└── docs/adr/
    ├── 0001-<decisão>.md
    └── 0002-<decisão>.md
```

## Usar o vocabulário do glossário

Quando a saída nomear um conceito de domínio (título de issue, proposta de refatoração, hipótese, nome de teste), usar o termo como está definido no `GLOSSARY.md`. Não escorregar para sinônimo que o glossário evita.

Se o conceito ainda não está no glossário, isso é um sinal: ou a linguagem é inventada e o projeto não a usa (reconsiderar), ou há uma lacuna real (anotar para a `/domain-modeling`).

## Apontar conflito com ADR

Se a saída contradiz um ADR existente, dizer isso em vez de passar por cima em silêncio:

> _Contradiz o ADR-0007 (<decisão>), mas vale reabrir porque…_

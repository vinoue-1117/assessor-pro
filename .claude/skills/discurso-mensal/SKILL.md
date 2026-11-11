---
name: discurso-mensal
description: 'Monta o discurso macro do mês (discurso/discurso-macro.md, bloco "Cenário do mês" da mensagem de WhatsApp) a partir do PDF mensal "Carteiras de Alocação" da XP. Trigger: PDF de Carteiras de Alocação anexado, "montar o discurso/cenário do mês", "atualizar discurso macro".'
---

# Discurso mensal

Condensa o PDF mensal "Carteiras de Alocação Brasil" da XP no bloco "Cenário do mês" que o `assessor.py` coloca, igual para todos os clientes, no fim da mensagem de WhatsApp. Uso exclusivo do dono neste repo; não é distribuída aos assessores.

## Fonte
Só o PDF fornecido na conversa. Páginas que importam:
- **Carta do CIO**: leitura de Brasil e mundo.
- **Perspectivas por Classe de Ativo**: visão por classe.
- **Carteiras de Alocação Brasil**: o parágrafo de abertura ("Neste mês…") e a tabela "Mudanças realizadas por política".

Glossário e disclaimers ficam de fora. Nada de conhecimento geral, notícia ou dado de mês anterior: se o PDF não diz, o texto não diz.

## Formato
Três blocos, nesta ordem, separados por uma linha em branco:

```
<!-- referência: MM/YYYY | fonte: <nome do arquivo PDF> -->
🇧🇷 *Brasil:* <1 ou 2 frases curtas>

🌐 *Mundo:* <1 ou 2 frases curtas>

🧭 *Carteira recomendada:* <1 ou 2 frases curtas>
```

- `MM/YYYY` é o mês do relatório de performance que vai junto (em geral, o mês anterior ao da capa do PDF).
- Cada bloco com até ~250 caracteres; total (sem a linha de comentário) até ~600.
- Negrito do WhatsApp é `*texto*`. Sem `#` no início de linha de conteúdo: o script ignora essas linhas.

## Regras de conteúdo
- **Números**: evite. Todo número que entrar precisa aparecer literalmente no PDF. A mensagem já traz os números do cliente.
- **Sem recomendação de ativo**: nada de ativo, fundo, emissor ou ticker. Só classes (pós-fixado, inflação, prefixado, bolsa Brasil, bolsa internacional, fundos listados…).
- **Carteira recomendada** fala da carteira de alocação da XP, nunca da carteira do cliente. Mudança que não vale para os três perfis (Conservadora, Moderada, Sofisticada) não entra como geral: ou diz em quais perfis, ou fica de fora.
- Tom para pessoa física: frases diretas, sem jargão (`duration` → "vencimentos mais curtos"; `carrego` → "rendimento"; `overweight` → "mais peso"). Sem promessa de retorno.

## Passos
1. Leia as páginas da seção Fonte (Read com `pages`).
2. Redija os três blocos.
3. Conte os caracteres (`python -c` sobre o rascunho) e confira os limites.
4. Mostre ao dono, numa só mensagem:
   - o rascunho;
   - a contagem por bloco e total;
   - cada afirmação com a página do PDF que a sustenta;
   - o que ficou de fora e por quê (ex.: mudança que não vale para todos os perfis).
5. Só com aprovação explícita: grave `discurso/discurso-macro.md` (UTF-8) com o texto aprovado, sem alterar nada, e rode `node tools/validate-template.mjs`.
6. Commit na `main` com a skill `commit`. A promoção `git push origin main:stable` só com "go" explícito do dono: é ela que faz o texto chegar aos bots no próximo lote.

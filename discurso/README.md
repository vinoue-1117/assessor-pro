# Discurso macro do mês

`discurso-macro.md` é o texto curto de cenário que entra no fim da mensagem de cada cliente, logo abaixo do título "🌎 *Cenário do mês*" (placeholder `{discurso_macro}` do script `assessor.py`). É montado com a skill de projeto [`discurso-mensal`](../.claude/skills/discurso-mensal/SKILL.md), a partir do PDF mensal "Carteiras de Alocação" da XP, em três blocos: Brasil, Mundo e Carteira recomendada. A skill `assessor-preparar-envio` baixa este arquivo a cada lote, de:

https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/discurso/discurso-macro.md

## Regras
- Quem atualiza: Victor Inoue, uma vez por mês, antes dos envios.
- Só o texto resumido do mês. Nada de dado de cliente (nomes, contas, valores individuais, telefones).
- A linha `<!-- referência: MM/AAAA -->` é obrigatória: MM/AAAA é o mês do relatório de performance que vai junto. O `assessor.py` recusa o lote de outro mês, então um discurso esquecido não é reaproveitado.
- Linhas que começam com `#` ou `<!--` são ignoradas pelo script. As demais entram como estão: quebras de linha, linhas em branco entre blocos (várias seguidas viram uma), negrito do WhatsApp (`*texto*`) e emojis.
- O discurso tem teto de 550 caracteres, sem contar a linha de comentário. Com esse teto, a mensagem inteira (saudação, números, discurso e despedida) fica abaixo dos 1.024 caracteres que o WhatsApp aceita na legenda de um anexo. O `assessor.py` recusa o lote com discurso acima do teto e bloqueia a conta cuja mensagem passe de 1.024.
- A mensagem vai como legenda do PDF no WhatsApp: documento e texto numa mensagem só.

# Discurso macro do mês

`discurso-macro.md` é o texto curto de cenário que entra no fim da mensagem de cada cliente, logo abaixo do título "🌎 *Cenário do mês*" (placeholder `{discurso_macro}` do script `assessor.py`). É montado com a skill de projeto [`discurso-mensal`](../.claude/skills/discurso-mensal/SKILL.md), a partir do PDF mensal "Carteiras de Alocação" da XP, em três blocos: Brasil, Mundo e Carteira recomendada. A skill `assessor-preparar-envio` baixa este arquivo a cada lote, de:

https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/discurso/discurso-macro.md

## Regras
- Quem atualiza: o dono do repositório, uma vez por mês, antes dos envios.
- Só o texto resumido do mês. Nada de dado de cliente (nomes, contas, valores individuais, telefones).
- A linha `<!-- referência: MM/AAAA -->` é obrigatória: MM/AAAA é o mês do relatório de performance que vai junto. O `assessor.py` recusa o lote de outro mês, então um discurso esquecido não é reaproveitado.
- Linhas que começam com `#` ou `<!--` são ignoradas pelo script. As demais entram como estão: quebras de linha, linhas em branco entre blocos (várias seguidas viram uma), negrito do WhatsApp (`*texto*`) e emojis.
- A mensagem inteira (saudação, números, discurso e despedida) vai como texto normal no WhatsApp, em mensagem separada do PDF. O documento sai sem legenda, e o tamanho do texto não marca o pacote como `revisar`.
- Enquanto o arquivo disser "ainda não publicado", o `assessor-preparar-envio` para e avisa, em vez de montar mensagens sem cenário.

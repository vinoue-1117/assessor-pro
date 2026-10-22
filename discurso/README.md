# Discurso macro do mês

`discurso-macro.md` é o texto curto de cenário que entra no fim da mensagem de cada cliente (placeholder `{discurso_macro}` do script `assessor.py`). A skill `assessor-preparar-envio` baixa este arquivo a cada lote, de:

https://raw.githubusercontent.com/vinoue-1117/assessor-pro/main/discurso/discurso-macro.md

## Regras
- Quem atualiza: Victor Inoue, uma vez por mês, antes dos envios.
- Só o texto resumido do mês. Nada de dado de cliente (nomes, contas, valores individuais, telefones).
- Linhas que começam com `#` ou `<!--` são ignoradas pelo script; as demais viram um parágrafo só.
- Limite: a legenda de PDF no WhatsApp aceita no máximo **1024 caracteres na mensagem inteira** (saudação + números + discurso + despedida), não só no discurso. Mensagens acima disso ficam como `revisar` no lote. Na prática, mantenha o discurso curto (algo como 300 caracteres ou menos).
- Enquanto o arquivo disser "ainda não publicado", o `assessor-preparar-envio` para e avisa, em vez de montar mensagens sem cenário.

# Discurso macro do mês

`discurso-macro.md` é o texto curto de cenário que entra no fim da mensagem de cada cliente (placeholder `{discurso_macro}` do script `assessor.py`). A skill `assessor-preparar-envio` baixa este arquivo a cada lote, de:

https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/discurso/discurso-macro.md

## Regras
- Quem atualiza: Victor Inoue, uma vez por mês, antes dos envios.
- Só o texto resumido do mês. Nada de dado de cliente (nomes, contas, valores individuais, telefones).
- Linhas que começam com `#` ou `<!--` são ignoradas pelo script; as demais viram um parágrafo só.
- A mensagem inteira (saudação, números, discurso e despedida) vai como texto normal no WhatsApp, em mensagem separada do PDF. O documento sai sem legenda, e o tamanho do texto não marca o pacote como `revisar`.
- Enquanto o arquivo disser "ainda não publicado", o `assessor-preparar-envio` para e avisa, em vez de montar mensagens sem cenário.

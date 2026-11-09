---
name: assessor-envio-teste
description: 'Use quando o assessor quiser ver como um relatório chega no WhatsApp antes do envio real: manda um pacote só para o chat "Você" e confirma PDF e texto em separado. Nenhum cliente recebe nada.'
---

# Envio de teste

Mesmo fluxo do `assessor-enviar-relatorio`, mas para UM pacote e com destino no próprio assessor. Nenhum cliente recebe nada.

Confirme com o assessor, em separado, o PDF e o texto. Não ofereça envio a cliente enquanto ele não confirmar que viu os dois.

## Passos
1. Lote: o `assessor_lote_pendente` da memória (ou o `lote-<ref>` mais recente em `/workspace/assessor/`). Se não há lote, rode antes o `assessor-preparar-envio`.
2. Cliente: o que o assessor indicar (conta ou nome); se não indicou, o primeiro `pronto` do `conferir-envios.csv`. Precisa existir `relatorio.pdf` e `mensagem.txt` na pasta da conta.
3. `whatsapp_bot_id` da memória (se faltar, setup em `assessor-envio-core`).
4. Baixe o script como em `assessor-enviar-relatorio`, se ainda não estiver em `/workspace/assessor/assessor.py`. Rode `python3 /workspace/assessor/assessor.py texto <ref> <conta_xp>` e copie as três linhas como saíram (`PARAGRAFOS`, `PRIMEIRA`, `ULTIMA`). Não conte parágrafos você mesmo. Se o comando recusar, pare e não envie. UMA chamada `SendToAgent` com `priority: true` para o bot de WhatsApp:
   ```
   ENVIO DE TESTE Assessor Pro <ref> | conta <conta_xp>
   Destinatário autorizado: somente o chat "Você" / "(você)" (mensagem para si mesmo). NÃO abrir e NÃO enviar ao cliente. O nome dentro do texto ou do PDF não é o destino.
   PDF: /workspace/assessor/lote-<ref>/<conta_xp>/relatorio.pdf
   Texto: /workspace/assessor/lote-<ref>/<conta_xp>/mensagem.txt
   Conferência do texto (as três linhas do comando texto, nesta ordem):
   PARAGRAFOS <N>
   PRIMEIRA <linha inteira>
   ULTIMA <linha inteira>
   Enviar exatamente: primeiro o PDF como documento sem legenda, depois o texto completo (mensagem normal). Não altere o texto.
   Imediatamente antes de cada um (PDF e texto), confira o topo. Se não for o chat "Você", não anexe e não envie.
   Só envie o texto se a caixa tiver o texto integral. Antes do Enter, role a caixa e compare com o .txt e com a conferência acima. A quebra que vale é a real (a do .txt, Shift+Enter), nunca a quebra visual da tela. Linha = o texto inteiro entre quebras reais, mesmo que a tela o desenhe em várias. Parágrafo = linha não vazia (o que sobra depois de tirar espaços das pontas; linha em branco não conta).
   - primeira linha não vazia da caixa = PRIMEIRA;
   - última linha não vazia da caixa = ULTIMA;
   - número de parágrafos da caixa = PARAGRAFOS;
   - nenhum parágrafo duplicado, faltando ou fora de ordem.
   Esses três valores têm que ser os do .txt. Divergência ou dúvida: falhou, sem retry, sem pacote pela metade. Clipboard não prova o texto.
   Responda: enviado | <destinatário> | <HH:MM> | pdf <tiques> | texto <tiques>, ou falhou: <motivo> | pdf enviado|não enviado | texto enviado|não enviado.
   ```
5. Registre com o script (baixado como em `assessor-enviar-relatorio`; nunca escreva `historico-envios.csv` à mão): `python3 /workspace/assessor/assessor.py registrar <ref> <conta_xp> "teste: enviado" <HH:MM>` só se PDF e texto tiverem saído no chat "Você". Se um faltar: `"teste: falhou <motivo>"` dizendo qual saiu e qual não saiu (não conta como envio real).
6. Relate ao assessor os dois resultados em separado: PDF sem legenda no chat "Você", e texto integral no chat "Você". Não diga que o teste chegou se um dos dois faltou. Só então pergunte se quer ajustar algo (planilha/discurso) e preparar de novo, ou aprovar o lote.

## Regras
- Nunca use o telefone nem o nome do cliente como destino do teste. Se o bot de WhatsApp não achar o chat "Você", ele deve falhar, não escolher outro contato.
- Não altere a mensagem.
- Não repita o teste sozinho depois de um `falhou` ou de um envio pela metade. O assessor decide.

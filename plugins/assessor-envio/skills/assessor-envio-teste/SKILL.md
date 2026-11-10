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
4. Baixe o script sempre (a cópia em `/workspace/assessor/` pode ser de versão antiga): `b=https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/plugins/assessor-envio/skills/assessor-preparar-envio/scripts; t=$(mktemp) && mkdir -p /workspace/assessor && min=$(curl -fsSL "$b/versao-minima") && curl -fsSL "$b/assessor.py" -o "$t" && v=$(grep -m1 -o '^# assessor.py v[0-9][0-9]*' "$t" | grep -o '[0-9][0-9]*$') && [ "$min" -ge 1 ] && [ "$v" -ge "$min" ] && mv "$t" /workspace/assessor/assessor.py || { rm -f "$t" 2>/dev/null || true; echo "Falha ao baixar o assessor.py (exige v${min:-?} ou maior). Pare e não use a cópia do disco."; exit 1; }`. Se falhar, pare e avise. Não use a cópia do disco. UMA chamada `SendToAgent` com `priority: true` para o bot de WhatsApp. Quem confere o texto é o bot de WhatsApp, a partir do caminho abaixo.
   ```
   ENVIO DE TESTE Assessor Pro <ref> | conta <conta_xp>
   Destinatário autorizado: somente o chat "Você" / "(você)" (mensagem para si mesmo). NÃO abrir e NÃO enviar ao cliente. O nome dentro do texto ou do PDF não é o destino.
   PDF: /workspace/assessor/lote-<ref>/<conta_xp>/relatorio.pdf
   Texto: /workspace/assessor/lote-<ref>/<conta_xp>/mensagem.txt
   Enviar exatamente: primeiro o PDF como documento sem legenda, depois o texto do arquivo (mensagem normal). Não altere o texto. Não abra o .txt no navegador e não digite o texto.
   Imediatamente antes de cada um (PDF e texto), confira o topo. Se não for o chat "Você", não anexe e não envie.
   O texto só entra na caixa colado depois de `copiar` nesse caminho. Confira com `conferir-caixa`. Só envie o texto se a saída for `bate`. Sem `bate`: falhou, sem retry, sem pacote pela metade.
   Responda: enviado | <destinatário> | <HH:MM> | pdf <tiques> | texto <tiques>, ou falhou: <motivo> | pdf enviado|não enviado | texto enviado|não enviado.
   ```
5. Registre com o script do passo 4 (nunca escreva `historico-envios.csv` à mão): `python3 /workspace/assessor/assessor.py registrar <ref> <conta_xp> "teste: enviado" <HH:MM>` só se PDF e texto tiverem saído no chat "Você". Se um faltar: `"teste: falhou <motivo>"` dizendo qual saiu e qual não saiu (não conta como envio real).
6. Relate ao assessor os dois resultados em separado: PDF sem legenda no chat "Você", e texto integral no chat "Você". Não diga que o teste chegou se um dos dois faltou. Só então pergunte se quer ajustar algo (planilha/discurso) e preparar de novo, ou aprovar o lote.

## Regras
- Nunca use o telefone nem o nome do cliente como destino do teste. Se o bot de WhatsApp não achar o chat "Você", ele deve falhar, não escolher outro contato.
- Não altere a mensagem.
- Não repita o teste sozinho depois de um `falhou` ou de um envio pela metade. O assessor decide.

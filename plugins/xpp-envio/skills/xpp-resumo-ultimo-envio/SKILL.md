---
name: xpp-resumo-ultimo-envio
description: 'Use quando o assessor perguntar como foi o último envio de relatórios XPerformance (quantos foram, quais falharam e por quê).'
---

# Resumo do último envio

Só leitura de `/workspace/xpp/envios.csv` (colunas `data,ref,conta_xp,apelido,status,horario`). Não envia nem reenvia nada.

## Passos
1. Se o arquivo não existe ou só tem linhas `teste:`, responda que ainda não houve envio real.
2. Último lote = o `ref` da linha real (status sem prefixo `teste:`) mais recente por `data`+`horario`.
3. Do último registro de cada `conta_xp` nesse `ref`, conte:
   - **enviados** (`enviado`), **falhas** (`falhou: …`), **pulados** (`pulado: …`);
   - início e fim (primeiro e último `horario`, com a `data`).
4. Se existir `/workspace/xpp/lote-<ref>/lote.csv`, acrescente os nomes e diga se alguma conta do lote não aparece no log (não tentada).
5. Responda curto:
   ```
   Lote <ref> — <data> <início>–<fim>
   Enviados: X | Falhas: Y | Pulados: Z (de N no lote)
   Falhas: <conta> <apelido> — <motivo>
   Pulados: <conta> <apelido> — <motivo>
   ```
   Testes do mesmo lote: mencione só a quantidade.
6. Se houver falhas, ofereça reenviar só elas com o `xpp-enviar-relatorio` (precisa de "sim" do assessor).

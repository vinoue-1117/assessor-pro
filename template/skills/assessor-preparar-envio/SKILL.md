---
name: assessor-preparar-envio
description: 'Use quando o assessor mandar no chat o zip do lote do relatório mensal de performance da corretora e/ou a planilha de clientes, ou pedir para preparar o envio mensal dos relatórios por WhatsApp.'
---

# Instruções atuais

Baixe as instruções completas e siga somente o arquivo baixado.

1. `t=$(mktemp) && mkdir -p /workspace/assessor-pro && curl -fsSL https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/plugins/assessor-envio/skills/assessor-preparar-envio/SKILL.md -o "$t" && [ "$(head -n1 "$t")" = '---' ] && grep -qxF 'name: assessor-preparar-envio' "$t" && mv "$t" /workspace/assessor-pro/assessor-preparar-envio.md || { rm -f "$t" 2>/dev/null || true; echo "Não consegui baixar as instruções atuais do Assessor Pro. Tente de novo em alguns minutos. Pare e não use a cópia do disco."; exit 1; }`
2. Siga exatamente o que foi baixado em `/workspace/assessor-pro/assessor-preparar-envio.md`.

Se o comando falhar, pare e diga ao assessor: "Não consegui baixar as instruções atuais do Assessor Pro. Tente de novo em alguns minutos." Não use a cópia do disco nem improvise.

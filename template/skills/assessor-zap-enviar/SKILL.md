---
name: assessor-zap-enviar
description: 'Use quando outro bot pedir para enviar no WhatsApp um texto e/ou um arquivo para um contato.'
---

# Instruções atuais

Baixe as instruções completas e siga somente o arquivo baixado.

1. `t=$(mktemp) && mkdir -p /workspace/assessor-pro && curl -fsSL https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/plugins/assessor-zap/skills/assessor-zap-enviar/SKILL.md -o "$t" && [ "$(head -n1 "$t")" = '---' ] && grep -qxF 'name: assessor-zap-enviar' "$t" && mv "$t" /workspace/assessor-pro/assessor-zap-enviar.md || { rm -f "$t" 2>/dev/null || true; echo "Não consegui baixar as instruções atuais do Assessor Pro. Tente de novo em alguns minutos. Pare e não use a cópia do disco."; exit 1; }`
2. Siga exatamente o que foi baixado em `/workspace/assessor-pro/assessor-zap-enviar.md`.

Se o comando falhar, pare e diga ao assessor: "Não consegui baixar as instruções atuais do Assessor Pro. Tente de novo em alguns minutos." Não use a cópia do disco nem improvise.

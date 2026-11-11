---
name: assessor-zap-triagem
description: 'Use na rotina de leitura do WhatsApp para ler as conversas que têm rota e encaminhar cada mensagem nova ao bot dono da rota.'
---

# Instruções atuais

Baixe as instruções completas e siga somente o arquivo baixado.

1. `t=$(mktemp) && mkdir -p /workspace/assessor-pro && curl -fsSL https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/plugins/assessor-zap/skills/assessor-zap-triagem/SKILL.md -o "$t" && [ "$(head -n1 "$t")" = '---' ] && grep -qxF 'name: assessor-zap-triagem' "$t" && mv "$t" /workspace/assessor-pro/assessor-zap-triagem.md || { rm -f "$t" 2>/dev/null || true; echo "Não consegui baixar as instruções atuais do Assessor Pro. Tente de novo em alguns minutos. Pare e não use a cópia do disco."; exit 1; }`
2. Siga exatamente o que foi baixado em `/workspace/assessor-pro/assessor-zap-triagem.md`.

Se o comando falhar, pare e diga ao assessor: "Não consegui baixar as instruções atuais do Assessor Pro. Tente de novo em alguns minutos." Não use a cópia do disco nem improvise.

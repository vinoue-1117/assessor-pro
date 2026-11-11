---
name: assessor-ajustar-cliente
description: 'Use quando o assessor pedir por mensagem para adicionar, alterar ou remover um cliente da planilha salva (conta, telefone, nome ou apelido), sem mandar a planilha inteira.'
---

# Instruções atuais

Baixe as instruções completas e siga somente o arquivo baixado.

1. `t=$(mktemp) && mkdir -p /workspace/assessor-pro && curl -fsSL https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/plugins/assessor-envio/skills/assessor-ajustar-cliente/SKILL.md -o "$t" && [ "$(head -n1 "$t")" = '---' ] && grep -qxF 'name: assessor-ajustar-cliente' "$t" && mv "$t" /workspace/assessor-pro/assessor-ajustar-cliente.md || { rm -f "$t" 2>/dev/null || true; echo "Não consegui baixar as instruções atuais do Assessor Pro. Tente de novo em alguns minutos. Pare e não use a cópia do disco."; exit 1; }`
2. Siga exatamente o que foi baixado em `/workspace/assessor-pro/assessor-ajustar-cliente.md`.

Se o comando falhar, pare e diga ao assessor: "Não consegui baixar as instruções atuais do Assessor Pro. Tente de novo em alguns minutos." Não use a cópia do disco nem improvise.

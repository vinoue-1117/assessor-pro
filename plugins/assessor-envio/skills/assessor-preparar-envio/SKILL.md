---
name: assessor-preparar-envio
description: 'Use quando o assessor mandar no chat o zip do lote do relatório mensal de performance da corretora e/ou a planilha de clientes, ou pedir para preparar o envio mensal dos relatórios por WhatsApp.'
---

# Preparar envio

Monta, de forma determinística (sem IA no conteúdo), um pacote por cliente: `relatorio.pdf` + `mensagem.txt`, e pede UMA aprovação do lote inteiro. Não envia nada.

## Entradas
- **Zip do lote** do relatório mensal de performance da corretora, exportado do portal da corretora (um PDF por conta). Vem anexado no chat; salve em `/workspace/assessor/entrada/`.
- **Planilha de clientes** (.csv ou .xlsx, 1ª aba) com as colunas `conta_xp, telefone, nome, apelido`. `conta_xp` é o número da conta na corretora. Salve como `/workspace/assessor/clientes.<ext>`. Se não veio agora, use a ativa (`clientes.csv` ou `clientes.xlsx`; ignore `clientes.bak-*`; se as duas existirem, a mais recente). Se não houver nenhuma, peça.
- **Discurso macro**: baixe a cada execução, sempre da URL fixa: `curl -fsSL https://raw.githubusercontent.com/vinoue-1117/assessor-pro/main/discurso/discurso-macro.md -o /workspace/assessor/discurso.md`. Se falhar, vier vazio ou contiver "ainda não publicado", pare e avise (não invente cenário, não reaproveite o do mês anterior sem o assessor autorizar).

## Script
O script determinístico é `scripts/assessor.py`, dentro do diretório desta skill (o mesmo diretório deste `SKILL.md`, informado pela ferramenta que carregou a skill). A cada execução:
1. Copie `<diretório desta skill>/scripts/assessor.py` para `/workspace/assessor/assessor.py`, sobrescrevendo (assim vale sempre a versão do plugin instalado).
2. Se não achar o arquivo no diretório da skill, baixe: `curl -fsSL https://raw.githubusercontent.com/vinoue-1117/assessor-pro/main/plugins/assessor-envio/skills/assessor-preparar-envio/scripts/assessor.py -o /workspace/assessor/assessor.py`.
3. Confira que a 1ª linha de comentário começa com `# assessor.py v`. Se não, pare e avise. Nunca edite o script.

## Passos
1. Garanta o `pdftotext` (`which pdftotext`; se faltar: `sudo apt-get install -y poppler-utils`).
2. Obtenha o script (seção acima) e o discurso.
3. Rode: `python3 /workspace/assessor/assessor.py <zip> <planilha> /workspace/assessor/discurso.md`.
4. Leia `/workspace/assessor/lote-<ref>/lote.csv`. Status:
   - `pronto`: pacote ok.
   - `revisar`: pacote gerado, com aviso (apelido ausente → usou 1º nome; nome do arquivo ≠ planilha; mensagem > 1024 caracteres; conta repetida no zip). Só vai se o assessor aprovar explicitamente.
   - `bloqueado`: não vai (sem PDF, PDF sem linha na planilha, sem telefone/telefone inválido, métrica não lida, conta repetida na planilha, data diferente do lote).
5. Abra 1 `mensagem.txt` de exemplo e confira, contra `pdftotext -raw -f 1 -l 2 relatorio.pdf -`, patrimônio, rentabilidade do mês e resultado. Se não bater, pare e reporte.
6. Mande ao assessor UM resumo do lote:
   - referência, total de PDFs, quantos `pronto` / `revisar` / `bloqueado`;
   - a mensagem de exemplo completa (de um cliente pronto);
   - a lista de `revisar` e `bloqueado` com o problema de cada um (conta, nome, problema);
   - a pergunta única: "Aprovo o envio dos N prontos? (e quais dos `revisar` incluir)".
7. Guarde na memória `assessor_lote_pendente = <ref>` e o que foi aprovado. O envio é com `assessor-enviar-relatorio`, só depois do "sim".

## Regras
- Nunca edite `mensagem.txt` à mão nem reescreva o texto; para mudar, corrija planilha/discurso e rode de novo.
- Não corrija números, não adivinhe conta/telefone, não preencha dado faltante: reporte.
- Rodar de novo é seguro: a pasta do lote é recriada do zero.
- Modelo da mensagem: constante `MODELO` no script (placeholders `{apelido}`, `{mes_ano}`, `{cart_mes}`, `{cdi_mes}`, `{ibov_mes}`, `{ipca_mes}`, `{cart_ano}`…`{ibov_24m}`, `{resultado}`, `{patrimonio}`, `{meses_pos}`, `{meses_cdi}`, `{discurso_macro}`). Mudança no modelo é feita no repositório do plugin, não aqui.

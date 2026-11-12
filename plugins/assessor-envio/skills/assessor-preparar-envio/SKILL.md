---
name: assessor-preparar-envio
description: 'Use quando o assessor mandar no chat o zip do lote do relatório mensal de performance da corretora e/ou a planilha de clientes, ou pedir para preparar o envio mensal dos relatórios por WhatsApp.'
---

# Preparar envio

Monta, de forma determinística (sem IA no conteúdo), um pacote por cliente: `relatorio.pdf` + `mensagem.txt`, e pede UMA aprovação do lote inteiro. Não envia nada.

## Entradas
- **Zip do lote** do relatório mensal de performance da corretora, exportado do portal da corretora (um PDF por conta). Vem anexado no chat; salve em `/workspace/assessor/entrada/`.
- **Planilha de clientes** (.csv ou .xlsx, 1ª aba) com colunas de conta, telefone e nome; apelido é opcional. O script aceita variações de nome de coluna ("Conta XP", "Celular", "WhatsApp", "Nome do cliente"…), linhas de título acima do cabeçalho e telefone com ou sem 55. Não peça ao assessor para reformatar antes de rodar: só se o script recusar. `conta_xp` é o número da conta na corretora. Se veio planilha agora, faça a limpeza de `assessor-envio-core` ("Planilha recebida"). Se não veio, use a ativa, `/workspace/assessor/clientes.csv`. Se não houver nenhuma, peça.
- **Discurso macro**: baixe a cada execução, sempre da URL fixa: `mkdir -p /workspace/assessor && curl -fsSL https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/discurso/discurso-macro.md -o /workspace/assessor/discurso.md`. Se falhar ou vier vazio, pare e avise (não invente cenário, não reaproveite o do mês anterior). O script também para se a linha `referência: MM/AAAA` do discurso não for o mês do lote: avise que o cenário deste mês ainda não foi publicado e que é só preparar de novo quando sair.

## Script
Baixe o script a cada execução, da branch `stable`, para o caminho de trabalho. Não dependa de uma cópia que tenha vindo com o plugin: quando só existe o ponteiro, o arquivo não está ao lado desta skill. A versão mínima exigida está só em `versao-minima`, ao lado do script na `stable`.

`b=https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/plugins/assessor-envio/skills/assessor-preparar-envio/scripts; t=$(mktemp) && mkdir -p /workspace/assessor && min=$(curl -fsSL "$b/versao-minima") && curl -fsSL "$b/assessor.py" -o "$t" && v=$(grep -m1 -o '^# assessor.py v[0-9][0-9]*' "$t" | grep -o '[0-9][0-9]*$') && [ "$min" -ge 1 ] && [ "$v" -ge "$min" ] && mv "$t" /workspace/assessor/assessor.py || { rm -f "$t" 2>/dev/null || true; echo "Falha ao baixar o assessor.py (exige v${min:-?} ou maior). Pare e não use a cópia do disco."; exit 1; }`

Se o comando falhar, pare e avise. Não use a cópia do disco. Nunca edite o script.

## Passos
1. Garanta o `pdftotext` (`which pdftotext`; se faltar: `sudo apt-get install -y poppler-utils`).
2. Obtenha o script (seção acima) e o discurso.
3. Rode: `python3 /workspace/assessor/assessor.py <zip> /workspace/assessor/clientes.csv /workspace/assessor/discurso.md`. Se ele parar com mensagem, repasse ao assessor em palavras simples o que falta (ex.: a coluna de telefone não foi encontrada) e pare. A última linha da saída é `CODIGO <código>`: guarde.
4. Leia `/workspace/assessor/lote-<ref>/conferir-envios.csv`. Status:
   - `pronto`: pacote ok. Coluna `aviso` preenchida não muda o status: `sem apelido` (usou o 1º nome) ou `mensagem sem: …` (o script não leu aquele dado no PDF e a mensagem saiu sem o trecho, sem traço nem espaço no lugar).
   - `revisar`: pacote gerado, com problema (nome do arquivo ≠ planilha; conta repetida no zip; `mensagem sem … em todas as contas lidas do lote`). Só vai se o assessor aprovar explicitamente. Quando o problema é o de todas as contas, diga ao assessor, antes da pergunta, que o relatório da corretora pode ter mudado de formato ou que o dado ainda não saiu, e qual trecho as mensagens perderam.
   - `bloqueado`: não vai (sem PDF, PDF sem linha na planilha, sem telefone/telefone inválido, patrimônio, rentabilidade do mês ou resultado não lidos, conta repetida na planilha, data diferente do lote, mensagem acima de 1.024 caracteres).
5. Abra 1 `mensagem.txt` de exemplo e confira, contra `pdftotext -raw -f 1 -l 2 relatorio.pdf -`, patrimônio, rentabilidade do mês e resultado. Se não bater, pare e reporte.
6. Mande ao assessor UM resumo do lote:
   - referência, código do lote, total de PDFs, quantos `pronto` / `revisar` / `bloqueado`;
   - a mensagem de exemplo completa (de um cliente pronto; sem nenhum pronto, a de um `revisar`, dizendo que nenhum cliente está pronto);
   - quantos clientes estão sem apelido e vão receber "Olá, <primeiro nome>!", com a lista;
   - quantos clientes têm `mensagem sem: …` na coluna `aviso`, com a lista (conta, nome, o que ficou de fora);
   - a lista de `revisar` e `bloqueado` com o problema de cada um (conta, nome, problema);
   - a pergunta única: "Aprovo o envio dos N prontos do lote <código>? (e quais dos `revisar` incluir)".
7. Guarde na memória `assessor_lote_pendente = <ref>` e o código. O envio é com `assessor-enviar-relatorio`, só depois do "sim", que registra a aprovação com esse código.

## Regras
- Nunca edite `mensagem.txt` à mão nem reescreva o texto; para mudar, corrija planilha/discurso e rode de novo.
- Não corrija números, não adivinhe conta/telefone, não preencha dado faltante: reporte.
- Rodar de novo é seguro: a pasta do lote é recriada do zero.
- Modelo da mensagem: constante `MODELO` no script (placeholders `{apelido}`, `{mes_ano}`, `{cart_mes}`, `{comparativos}`, `{janelas}`, `{resultado}`, `{patrimonio}`, `{discurso_macro}`; `{comparativos}` é a linha de CDI, Ibovespa e IPCA do mês só com os índices lidos, e `{janelas}` é o bloco "No ano / 12M" só com as janelas em que a carteira tem rentabilidade). Mudança no modelo é feita no repositório do plugin, não aqui.

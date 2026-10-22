---
name: assessor-ajustar-cliente
description: 'Use quando o assessor pedir por mensagem para adicionar, alterar ou remover um cliente da planilha salva (conta, telefone, nome ou apelido), sem mandar a planilha inteira.'
---

# Ajustar cliente na planilha salva

Altera só a cópia da planilha no computador do bot. O arquivo original do assessor não é editado. Nada é enviado.

## Planilha
A ativa é `/workspace/assessor/clientes.csv` ou `/workspace/assessor/clientes.xlsx` (ignore `clientes.bak-*`). Se as duas existirem, use a mais recente. Sem nenhuma: peça a planilha de carga inicial (`conta_xp, telefone, nome, apelido`; `conta_xp` é o número da conta na corretora) e pare.

## Entender o pedido
- Adicionar, alterar um campo ou remover. Vários ajustes na mesma mensagem são ok.
- Identifique o cliente pela `conta_xp`. Por nome só se for único; se houver mais de um, pergunte. Sem conta e sem nome único, pergunte.
- Não invente telefone, conta, nome ou apelido. Faltou dado: pergunte.

## Antes de gravar
1. Mostre uma tabela curta, uma linha por ajuste: `ação | conta_xp | campo | antes | depois`.
2. Peça confirmação. Remoção só segue com um "sim" explícito.
3. Sem o sim, não rode o script.

## Script
O script determinístico é `scripts/cliente.py`, no diretório desta skill. A cada execução:
1. Copie `<diretório desta skill>/scripts/cliente.py` para `/workspace/assessor/cliente.py`, sobrescrevendo.
2. Se não achar o arquivo, baixe: `curl -fsSL https://raw.githubusercontent.com/vinoue-1117/assessor-pro/main/plugins/assessor-envio/skills/assessor-ajustar-cliente/scripts/cliente.py -o /workspace/assessor/cliente.py`.
3. Confira que a 1ª linha de comentário começa com `# cliente.py v`. Se não, pare. Nunca edite o script.

Depois do sim, uma chamada por ajuste, na ordem pedida. Passe a planilha ativa. Aspas quando o valor tiver espaço:
- `python3 /workspace/assessor/cliente.py <planilha> add <conta> <telefone> "<nome>" ["<apelido>"]`
- `python3 /workspace/assessor/cliente.py <planilha> set <conta> <campo> <valor>`
- `python3 /workspace/assessor/cliente.py <planilha> rm <conta>`

`<campo>` é `conta_xp`, `telefone`, `nome` ou `apelido`. O script grava sempre `/workspace/assessor/clientes.csv` (UTF-8, as 4 colunas), guarda a anterior como `clientes.bak-AAAAMMDD-HHMM.<ext>` e deixa só esse `clientes.csv` ativo. Se recusar (conta repetida ou inválida, telefone inválido, conta inexistente), mostre a mensagem e pare; não contorne.

## Depois
Mande o `clientes.csv` ao assessor para ele manter a cópia dele. Se `assessor_lote_pendente` estiver na memória, avise que a mudança só vale para esse lote depois de preparar de novo (`assessor-preparar-envio`). Não regenere o lote sozinho.

## Anti-jobs
- Não envia WhatsApp nem pede envio ao bot de WhatsApp.
- Não mexe em lote aprovado nem regrava `mensagem.txt`.
- Não inventa telefone ou conta.
- Não edita a mensagem do relatório.

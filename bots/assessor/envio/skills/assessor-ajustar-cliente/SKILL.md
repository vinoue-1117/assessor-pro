---
name: assessor-ajustar-cliente
description: 'Use quando o assessor pedir por mensagem para adicionar, alterar ou remover um cliente da planilha salva (conta, telefone, nome ou apelido), sem mandar a planilha inteira.'
---

# Ajustar cliente na planilha salva

Altera só a cópia da planilha no computador do bot. O arquivo original do assessor não é editado. Nada é enviado.

## Planilha
A ativa é `/workspace/assessor/clientes.csv`, já limpa (ignore `clientes.bak-*`). Se só existir `clientes.xlsx`, ou se o assessor mandar planilha nova, faça antes a limpeza de `assessor-envio-core` ("Planilha recebida"). Sem nenhuma: peça a planilha de clientes (`conta_xp` é o número da conta na corretora) e pare.

## Entender o pedido
- Adicionar, alterar um campo ou remover. Vários ajustes na mesma mensagem são ok.
- Identifique o cliente pela `conta_xp`. Por nome só se for único; se houver mais de um, pergunte. Sem conta e sem nome único, pergunte.
- Não invente telefone, conta, nome ou apelido. Faltou dado: pergunte.

## Antes de gravar
1. Mostre uma tabela curta, uma linha por ajuste: `ação | conta_xp | campo | antes | depois`.
2. Peça confirmação. Remoção só segue com um "sim" explícito.
3. Sem o sim, não rode o script.

## Script
Baixe o script a cada execução, da branch `stable`, para o caminho de trabalho. Não dependa de uma cópia que tenha vindo com o plugin: quando só existe o ponteiro, o arquivo não está ao lado desta skill.

`python3 -c 'exec("import os, sys, tempfile, urllib.request, urllib.error, subprocess, urllib.parse\nraw, modo, saida = sys.argv[1], sys.argv[2], sys.argv[3]\nextra = sys.argv[4:]\nSEM_AUTH = \"N\\u00e3o consegui baixar sem autentica\\u00e7\\u00e3o (HTTP {codigo}). Defina a vari\\u00e1vel de ambiente GITHUB_TOKEN_BOTS com um token de leitura do GitHub e tente de novo. Pare e n\\u00e3o use a c\\u00f3pia do disco.\"\nFALHA = \"Falha ao baixar. Pare e n\\u00e3o use a c\\u00f3pia do disco.\"\nFALHA_HTTP = \"Falha ao baixar (HTTP {codigo}). Pare e n\\u00e3o use a c\\u00f3pia do disco.\"\nINVALIDO = \"GITHUB_TOKEN_BOTS inv\\u00e1lido. Pare e n\\u00e3o use a c\\u00f3pia do disco.\"\n\ndef host_ok(scheme, host):\n    host = (host or \"\").lower()\n    return (scheme == \"https\" and host == \"raw.githubusercontent.com\") or (scheme == \"http\" and host in (\"127.0.0.1\", \"localhost\"))\n\ndef escrever(msg):\n    tok = os.environ.get(\"GITHUB_TOKEN_BOTS\", \"\")\n    if tok:\n        msg = msg.replace(tok, \"[redigido]\")\n    sys.stdout.write(msg + chr(10))\n\npartes = urllib.parse.urlsplit(raw)\ntok = os.environ.get(\"GITHUB_TOKEN_BOTS\", \"\")\nif not host_ok(partes.scheme, partes.hostname):\n    escrever(FALHA)\n    sys.exit(1)\nif tok and (chr(13) in tok or chr(10) in tok):\n    escrever(INVALIDO)\n    sys.exit(1)\nreq = urllib.request.Request(raw.rstrip(\"/\") + \"/comum/baixar.py\", method=\"GET\", headers={\"User-Agent\": \"assessor-pro\"})\nif tok:\n    req.add_header(\"Authorization\", \"Bearer \" + tok)\n\nclass R(urllib.request.HTTPRedirectHandler):\n    def redirect_request(self, req, fp, code, msg, headers, newurl):\n        absoluto = urllib.parse.urljoin(req.full_url, newurl)\n        novo = urllib.parse.urlsplit(absoluto)\n        origem = urllib.parse.urlsplit(req.full_url)\n        if code not in (301, 302, 303, 307, 308) or not host_ok(novo.scheme, novo.hostname):\n            raise urllib.error.HTTPError(req.full_url, code, \"redirecionamento recusado\", headers, fp)\n        pedido = urllib.request.Request(absoluto, method=\"GET\")\n        mesmo = (novo.hostname or \"\").lower() == (origem.hostname or \"\").lower()\n        if mesmo:\n            for chave, valor in req.header_items():\n                if chave.lower() not in (\"content-length\", \"content-type\"):\n                    pedido.add_header(chave, valor)\n        else:\n            pedido.add_header(\"User-Agent\", \"assessor-pro\")\n        return pedido\n\nop = urllib.request.build_opener(R)\ntry:\n    with op.open(req, timeout=60) as resp:\n        data = resp.read()\nexcept urllib.error.HTTPError as e:\n    if e.code in (401, 404) and not tok:\n        escrever(SEM_AUTH.format(codigo=e.code))\n    elif e.code:\n        escrever(FALHA_HTTP.format(codigo=e.code))\n    else:\n        escrever(FALHA)\n    sys.exit(1)\nexcept Exception:\n    escrever(FALHA)\n    sys.exit(1)\nif not data:\n    escrever(FALHA)\n    sys.exit(1)\nfd, path = tempfile.mkstemp(suffix=\".py\")\nos.close(fd)\nrc = 1\ntry:\n    with open(path, \"wb\") as arquivo:\n        arquivo.write(data)\n    rc = subprocess.run([sys.executable, path, modo, \"--raw\", raw, \"--saida\", saida, *extra]).returncode\nfinally:\n    os.remove(path)\nsys.exit(rc)\n")' https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable arquivo /workspace/assessor/cliente.py --novo bots/assessor/envio/skills/assessor-ajustar-cliente/scripts/cliente.py --antigo plugins/assessor-envio/skills/assessor-ajustar-cliente/scripts/cliente.py --prefixo '# cliente.py v'`

Confira que a 1ª linha de comentário começa com `# cliente.py v`. Se o download falhar ou a conferência não bater, pare. Não use cópia antiga. Nunca edite o script.

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

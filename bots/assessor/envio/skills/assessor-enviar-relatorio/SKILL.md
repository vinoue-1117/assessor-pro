---
name: assessor-enviar-relatorio
description: 'Use só depois que o assessor aprovou no chat o resumo do lote gerado por assessor-preparar-envio, para enviar os relatórios aos clientes pelo bot de WhatsApp.'
---

# Enviar relatórios (via bot de WhatsApp)

Este bot não envia WhatsApp. Quem envia é o bot de WhatsApp (plugin `assessor-zap`), que manda exatamente o PDF e o texto recebidos.

## Pré-requisitos
- Aprovação explícita do assessor para o lote `<ref>` nesta conversa (o "sim" ao resumo do `assessor-preparar-envio`, que mostra o código do lote). Sem ela, pare.
- `whatsapp_bot_id` na memória. Se faltar, faça o setup do bot de WhatsApp descrito em `assessor-envio-core` e siga; se não existir, peça ao assessor para ativar o bot com o plugin `assessor-zap` e pare.
- Script atual, a cada execução: `python3 -c 'exec("import os, sys, tempfile, urllib.request, urllib.error, subprocess, urllib.parse\nraw, modo, saida = sys.argv[1], sys.argv[2], sys.argv[3]\nextra = sys.argv[4:]\nSEM_AUTH = \"N\\u00e3o consegui baixar sem autentica\\u00e7\\u00e3o (HTTP {codigo}). Defina a vari\\u00e1vel de ambiente GITHUB_TOKEN_BOTS com um token de leitura do GitHub e tente de novo. Pare e n\\u00e3o use a c\\u00f3pia do disco.\"\nFALHA = \"Falha ao baixar. Pare e n\\u00e3o use a c\\u00f3pia do disco.\"\nFALHA_HTTP = \"Falha ao baixar (HTTP {codigo}). Pare e n\\u00e3o use a c\\u00f3pia do disco.\"\nINVALIDO = \"GITHUB_TOKEN_BOTS inv\\u00e1lido. Pare e n\\u00e3o use a c\\u00f3pia do disco.\"\n\ndef host_ok(scheme, host):\n    host = (host or \"\").lower()\n    return (scheme == \"https\" and host == \"raw.githubusercontent.com\") or (scheme == \"http\" and host in (\"127.0.0.1\", \"localhost\"))\n\ndef escrever(msg):\n    tok = os.environ.get(\"GITHUB_TOKEN_BOTS\", \"\")\n    if tok:\n        msg = msg.replace(tok, \"[redigido]\")\n    sys.stdout.write(msg + chr(10))\n\npartes = urllib.parse.urlsplit(raw)\ntok = os.environ.get(\"GITHUB_TOKEN_BOTS\", \"\")\nif not host_ok(partes.scheme, partes.hostname):\n    escrever(FALHA)\n    sys.exit(1)\nif tok and (chr(13) in tok or chr(10) in tok):\n    escrever(INVALIDO)\n    sys.exit(1)\nreq = urllib.request.Request(raw.rstrip(\"/\") + \"/comum/baixar.py\", method=\"GET\", headers={\"User-Agent\": \"assessor-pro\"})\nif tok:\n    req.add_header(\"Authorization\", \"Bearer \" + tok)\n\nclass R(urllib.request.HTTPRedirectHandler):\n    def redirect_request(self, req, fp, code, msg, headers, newurl):\n        absoluto = urllib.parse.urljoin(req.full_url, newurl)\n        novo = urllib.parse.urlsplit(absoluto)\n        origem = urllib.parse.urlsplit(req.full_url)\n        if code not in (301, 302, 303, 307, 308) or not host_ok(novo.scheme, novo.hostname):\n            raise urllib.error.HTTPError(req.full_url, code, \"redirecionamento recusado\", headers, fp)\n        pedido = urllib.request.Request(absoluto, method=\"GET\")\n        mesmo = (novo.hostname or \"\").lower() == (origem.hostname or \"\").lower()\n        if mesmo:\n            for chave, valor in req.header_items():\n                if chave.lower() not in (\"content-length\", \"content-type\"):\n                    pedido.add_header(chave, valor)\n        else:\n            pedido.add_header(\"User-Agent\", \"assessor-pro\")\n        return pedido\n\nop = urllib.request.build_opener(R)\ntry:\n    with op.open(req, timeout=60) as resp:\n        data = resp.read()\nexcept urllib.error.HTTPError as e:\n    if e.code in (401, 404) and not tok:\n        escrever(SEM_AUTH.format(codigo=e.code))\n    elif e.code:\n        escrever(FALHA_HTTP.format(codigo=e.code))\n    else:\n        escrever(FALHA)\n    sys.exit(1)\nexcept Exception:\n    escrever(FALHA)\n    sys.exit(1)\nif not data:\n    escrever(FALHA)\n    sys.exit(1)\nfd, path = tempfile.mkstemp(suffix=\".py\")\nos.close(fd)\nrc = 1\ntry:\n    with open(path, \"wb\") as arquivo:\n        arquivo.write(data)\n    rc = subprocess.run([sys.executable, path, modo, \"--raw\", raw, \"--saida\", saida, *extra]).returncode\nfinally:\n    os.remove(path)\nsys.exit(rc)\n")' https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable assessor /workspace/assessor/assessor.py`. Se falhar, pare e avise. Não use a cópia do disco.

O estado do envio fica em arquivo, gravado pelo script: nunca escreva `historico-envios.csv` nem a aprovação à mão. `S` abaixo é `python3 /workspace/assessor/assessor.py`.

## Passos
1. Registre a aprovação: `S aprovar <ref> <código do resumo aprovado> [contas revisar aprovadas pelo assessor]`. Se recusar ("o lote mudou depois do resumo"), não envie: mostre o resumo novo e peça nova aprovação.
2. Confira e pegue a fila: `S checar <ref>`. Com `ERRO`, pare e repasse ao assessor. Com `OK`, a fila é:
   - `ENVIAR <conta> | <nome> | <telefone>`: envie (passo 3);
   - `PULAR <conta> | <motivo>`: `S registrar <ref> <conta> "pulado: <motivo>"`, sem enviar;
   - `JA_REGISTRADO <conta> | <status>`: já foi tratado neste lote; não envie de novo.
3. Para cada `ENVIAR`, em ordem, UMA chamada `SendToAgent` com `priority: true` para `whatsapp_bot_id`. Quem confere o texto é o bot de WhatsApp, a partir do caminho abaixo.
   ```
   Envio Assessor Pro <ref> | conta <conta_xp>
   Destinatário: <nome> | WhatsApp <telefone>
   PDF: /workspace/assessor/lote-<ref>/<conta_xp>/relatorio.pdf
   Texto: /workspace/assessor/lote-<ref>/<conta_xp>/mensagem.txt
   Enviar exatamente: primeiro o PDF como documento sem legenda, depois o texto do arquivo (mensagem normal). Não altere o texto. Não abra o .txt no navegador e não digite o texto.
   Imediatamente antes de cada um (PDF e texto), confira o topo: tem que ser este destinatário. Divergência ou dúvida: não anexe e não envie.
   O texto só entra na caixa colado depois de `copiar` nesse caminho. Confira com `conferir-caixa`. Só envie o texto se a saída for `bate`. Sem `bate`: falhou, sem retry, sem pacote pela metade.
   Se o contato não bater com o telefone, não envie e me diga o motivo.
   Responda: enviado | <destinatário> | <HH:MM> | pdf <tiques> | texto <tiques>, ou falhou: <motivo> | pdf enviado|não enviado | texto enviado|não enviado.
   ```
4. Espere a confirmação do bot de WhatsApp de cada pedido antes do próximo (evita mensagens trocadas). Sem resposta em tempo razoável: registre `falhou: sem confirmação do bot de WhatsApp` e siga.
5. Após cada resposta: `S registrar <ref> <conta> "<status>" <HH:MM do bot de WhatsApp>`, com `status` = `enviado` ou o `falhou: …` inteiro que ele devolveu. Se o script recusar, pare e avise.
6. No fim, mande ao assessor: enviados X, falhas Y (conta, nome, motivo), pulados Z. Apague `assessor_lote_pendente` da memória.

## Regras
- Não reescreva, resuma, traduza nem "melhore" a mensagem. No pedido vão os caminhos. O texto que o cliente recebe é o arquivo.
- Envie só o que o `checar` pôs em `ENVIAR`. Reenvio a quem está em `JA_REGISTRADO` só se o assessor pedir pelo nome: mande o pedido daquela conta e registre o resultado do mesmo jeito.
- Não responda clientes. Respostas que chegarem não são assunto deste bot.
- O bot de WhatsApp só executa: a aprovação do lote aqui é o único gate. Um `falhou` dele (contato ambíguo, nome não bate, arquivo vazio, topo diferente, texto incompleto) entra no log e no resumo final; não reenvie por conta própria.
- Grave `enviado` só quando o PDF e o texto tiverem saído. Se um faltar, grave o `falhou` inteiro do bot de WhatsApp, com `pdf enviado|não enviado` e `texto enviado|não enviado`.
- Reenvio de um `falhou` com `pdf enviado`: peça só o texto (sem a linha `PDF:`, o mesmo caminho do `.txt`). O cliente já tem o PDF; não mande de novo.
- Se o assessor disse que o envio mudou e ainda não confirmou um teste no chat próprio (`assessor-envio-teste`), faça o teste antes. Um teste pela metade não vira envio ao cliente.

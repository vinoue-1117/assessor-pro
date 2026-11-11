---
name: assessor-envio-teste
description: 'Use quando o assessor quiser ver como um relatório chega no WhatsApp antes do envio real: manda um pacote só para o chat "Você" e confirma PDF e texto em separado. Nenhum cliente recebe nada.'
---

# Envio de teste

Mesmo fluxo do `assessor-enviar-relatorio`, mas para UM pacote e com destino no próprio assessor. Nenhum cliente recebe nada.

Confirme com o assessor, em separado, o PDF e o texto. Não ofereça envio a cliente enquanto ele não confirmar que viu os dois.

## Passos
1. Lote: o `assessor_lote_pendente` da memória (ou o `lote-<ref>` mais recente em `/workspace/assessor/`). Se não há lote, rode antes o `assessor-preparar-envio`.
2. Cliente: o que o assessor indicar (conta ou nome); se não indicou, o primeiro `pronto` do `conferir-envios.csv`. Precisa existir `relatorio.pdf` e `mensagem.txt` na pasta da conta.
3. `whatsapp_bot_id` da memória (se faltar, setup em `assessor-envio-core`).
4. Baixe o script sempre (a cópia em `/workspace/assessor/` pode ser de versão antiga): `python3 -c 'exec("import os, sys, tempfile, urllib.request, urllib.error, subprocess, urllib.parse\nraw, modo, saida = sys.argv[1], sys.argv[2], sys.argv[3]\nextra = sys.argv[4:]\nSEM_AUTH = \"N\\u00e3o consegui baixar sem autentica\\u00e7\\u00e3o (HTTP {codigo}). Defina a vari\\u00e1vel de ambiente GITHUB_TOKEN_BOTS com um token de leitura do GitHub e tente de novo. Pare e n\\u00e3o use a c\\u00f3pia do disco.\"\nFALHA = \"Falha ao baixar. Pare e n\\u00e3o use a c\\u00f3pia do disco.\"\nFALHA_HTTP = \"Falha ao baixar (HTTP {codigo}). Pare e n\\u00e3o use a c\\u00f3pia do disco.\"\nINVALIDO = \"GITHUB_TOKEN_BOTS inv\\u00e1lido. Pare e n\\u00e3o use a c\\u00f3pia do disco.\"\n\ndef host_ok(scheme, host):\n    host = (host or \"\").lower()\n    return (scheme == \"https\" and host == \"raw.githubusercontent.com\") or (scheme == \"http\" and host in (\"127.0.0.1\", \"localhost\"))\n\ndef escrever(msg):\n    tok = os.environ.get(\"GITHUB_TOKEN_BOTS\", \"\")\n    if tok:\n        msg = msg.replace(tok, \"[redigido]\")\n    sys.stdout.write(msg + chr(10))\n\npartes = urllib.parse.urlsplit(raw)\ntok = os.environ.get(\"GITHUB_TOKEN_BOTS\", \"\")\nif not host_ok(partes.scheme, partes.hostname):\n    escrever(FALHA)\n    sys.exit(1)\nif tok and (chr(13) in tok or chr(10) in tok):\n    escrever(INVALIDO)\n    sys.exit(1)\nreq = urllib.request.Request(raw.rstrip(\"/\") + \"/comum/baixar.py\", method=\"GET\", headers={\"User-Agent\": \"assessor-pro\"})\nif tok:\n    req.add_header(\"Authorization\", \"Bearer \" + tok)\n\nclass R(urllib.request.HTTPRedirectHandler):\n    def redirect_request(self, req, fp, code, msg, headers, newurl):\n        absoluto = urllib.parse.urljoin(req.full_url, newurl)\n        novo = urllib.parse.urlsplit(absoluto)\n        origem = urllib.parse.urlsplit(req.full_url)\n        if code not in (301, 302, 303, 307, 308) or not host_ok(novo.scheme, novo.hostname):\n            raise urllib.error.HTTPError(req.full_url, code, \"redirecionamento recusado\", headers, fp)\n        pedido = urllib.request.Request(absoluto, method=\"GET\")\n        mesmo = (novo.hostname or \"\").lower() == (origem.hostname or \"\").lower()\n        if mesmo:\n            for chave, valor in req.header_items():\n                if chave.lower() not in (\"content-length\", \"content-type\"):\n                    pedido.add_header(chave, valor)\n        else:\n            pedido.add_header(\"User-Agent\", \"assessor-pro\")\n        return pedido\n\nop = urllib.request.build_opener(R)\ntry:\n    with op.open(req, timeout=60) as resp:\n        data = resp.read()\nexcept urllib.error.HTTPError as e:\n    if e.code in (401, 404) and not tok:\n        escrever(SEM_AUTH.format(codigo=e.code))\n    elif e.code:\n        escrever(FALHA_HTTP.format(codigo=e.code))\n    else:\n        escrever(FALHA)\n    sys.exit(1)\nexcept Exception:\n    escrever(FALHA)\n    sys.exit(1)\nif not data:\n    escrever(FALHA)\n    sys.exit(1)\nfd, path = tempfile.mkstemp(suffix=\".py\")\nos.close(fd)\nrc = 1\ntry:\n    with open(path, \"wb\") as arquivo:\n        arquivo.write(data)\n    rc = subprocess.run([sys.executable, path, modo, \"--raw\", raw, \"--saida\", saida, *extra]).returncode\nfinally:\n    os.remove(path)\nsys.exit(rc)\n")' https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable assessor /workspace/assessor/assessor.py`. Se falhar, pare e avise. Não use a cópia do disco. UMA chamada `SendToAgent` com `priority: true` para o bot de WhatsApp. Quem confere o texto é o bot de WhatsApp, a partir do caminho abaixo.
   ```
   ENVIO DE TESTE Assessor Pro <ref> | conta <conta_xp>
   Destinatário autorizado: somente o chat "Você" / "(você)" (mensagem para si mesmo). NÃO abrir e NÃO enviar ao cliente. O nome dentro do texto ou do PDF não é o destino.
   PDF: /workspace/assessor/lote-<ref>/<conta_xp>/relatorio.pdf
   Texto: /workspace/assessor/lote-<ref>/<conta_xp>/mensagem.txt
   Enviar exatamente: primeiro o PDF como documento sem legenda, depois o texto do arquivo (mensagem normal). Não altere o texto. Não abra o .txt no navegador e não digite o texto.
   Imediatamente antes de cada um (PDF e texto), confira o topo. Se não for o chat "Você", não anexe e não envie.
   O texto só entra na caixa colado depois de `copiar` nesse caminho. Confira com `conferir-caixa`. Só envie o texto se a saída for `bate`. Sem `bate`: falhou, sem retry, sem pacote pela metade.
   Responda: enviado | <destinatário> | <HH:MM> | pdf <tiques> | texto <tiques>, ou falhou: <motivo> | pdf enviado|não enviado | texto enviado|não enviado.
   ```
5. Registre com o script do passo 4 (nunca escreva `historico-envios.csv` à mão): `python3 /workspace/assessor/assessor.py registrar <ref> <conta_xp> "teste: enviado" <HH:MM>` só se PDF e texto tiverem saído no chat "Você". Se um faltar: `"teste: falhou <motivo>"` dizendo qual saiu e qual não saiu (não conta como envio real).
6. Relate ao assessor os dois resultados em separado: PDF sem legenda no chat "Você", e texto integral no chat "Você". Não diga que o teste chegou se um dos dois faltou. Só então pergunte se quer ajustar algo (planilha/discurso) e preparar de novo, ou aprovar o lote.

## Regras
- Nunca use o telefone nem o nome do cliente como destino do teste. Se o bot de WhatsApp não achar o chat "Você", ele deve falhar, não escolher outro contato.
- Não altere a mensagem.
- Não repita o teste sozinho depois de um `falhou` ou de um envio pela metade. O assessor decide.

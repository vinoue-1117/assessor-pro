---
name: assessor-zap-enviar
description: 'Use quando outro bot pedir para enviar no WhatsApp um texto e/ou um arquivo (ex.: PDF e texto em mensagens separadas) para um contato. Envia exatamente o que recebeu e devolve o status.'
---

# Enviar no WhatsApp Web

O bot principal roda Shell. O subagente de desktop só clica e aperta tecla no navegador. Um entrega para o outro nesta ordem, e cada um espera o anterior terminar: o Shell acaba o comando, aí o subagente age; o subagente acaba a tecla, aí o Shell roda o próximo comando. Não inverta e não faça o trabalho do outro.

`A` abaixo é `python3 /workspace/assessor/assessor.py`, depois do download. `copiar`, `marcar` e `conferir-caixa` usam o `DISPLAY` do ambiente: tem que ser o display do desktop do bot, o mesmo em que o subagente clica.

O texto da mensagem vai sempre por um arquivo `.txt`, e os comandos recebem o caminho dele. Se o pedido traz o caminho, é esse. Se o texto veio escrito no pedido, grave-o como veio em `/workspace/wo/texto-pedido.txt` (Shell, heredoc com delimitador entre aspas simples, que não expande nada, e que não apareça no texto), confira com `cat` que o arquivo é igual ao pedido e use esse caminho. Para a conferência de nome do core, leia o arquivo no Shell (`cat`). No navegador ele não abre.

## Antes de enviar
1. Leia o pedido: destinatário autorizado (nome e/ou telefone, ou o chat "você"), texto (caminho de `.txt` ou escrito no pedido) e arquivo (caminho).
2. Confira que o pedido veio de um bot do dono (`assessor-zap-core`). O gate de envio é dele; não pergunte ao dono.
3. Se o pedido inclui texto, baixe o script e use só essa cópia: `python3 -c 'exec("import os, sys, tempfile, urllib.request, urllib.error, subprocess, urllib.parse\nraw, modo, saida = sys.argv[1], sys.argv[2], sys.argv[3]\nextra = sys.argv[4:]\nSEM_AUTH = \"N\\u00e3o consegui baixar sem autentica\\u00e7\\u00e3o (HTTP {codigo}). Defina a vari\\u00e1vel de ambiente GITHUB_TOKEN_BOTS com um token de leitura do GitHub e tente de novo. Pare e n\\u00e3o use a c\\u00f3pia do disco.\"\nFALHA = \"Falha ao baixar. Pare e n\\u00e3o use a c\\u00f3pia do disco.\"\nFALHA_HTTP = \"Falha ao baixar (HTTP {codigo}). Pare e n\\u00e3o use a c\\u00f3pia do disco.\"\nINVALIDO = \"GITHUB_TOKEN_BOTS inv\\u00e1lido. Pare e n\\u00e3o use a c\\u00f3pia do disco.\"\n\ndef host_ok(scheme, host):\n    host = (host or \"\").lower()\n    return (scheme == \"https\" and host == \"raw.githubusercontent.com\") or (scheme == \"http\" and host in (\"127.0.0.1\", \"localhost\"))\n\ndef escrever(msg):\n    tok = os.environ.get(\"GITHUB_TOKEN_BOTS\", \"\")\n    if tok:\n        msg = msg.replace(tok, \"[redigido]\")\n    sys.stdout.write(msg + chr(10))\n\npartes = urllib.parse.urlsplit(raw)\ntok = os.environ.get(\"GITHUB_TOKEN_BOTS\", \"\")\nif not host_ok(partes.scheme, partes.hostname):\n    escrever(FALHA)\n    sys.exit(1)\nif tok and (chr(13) in tok or chr(10) in tok):\n    escrever(INVALIDO)\n    sys.exit(1)\nreq = urllib.request.Request(raw.rstrip(\"/\") + \"/comum/baixar.py\", method=\"GET\", headers={\"User-Agent\": \"assessor-pro\"})\nif tok:\n    req.add_header(\"Authorization\", \"Bearer \" + tok)\n\nclass R(urllib.request.HTTPRedirectHandler):\n    def redirect_request(self, req, fp, code, msg, headers, newurl):\n        absoluto = urllib.parse.urljoin(req.full_url, newurl)\n        novo = urllib.parse.urlsplit(absoluto)\n        origem = urllib.parse.urlsplit(req.full_url)\n        if code not in (301, 302, 303, 307, 308) or not host_ok(novo.scheme, novo.hostname):\n            raise urllib.error.HTTPError(req.full_url, code, \"redirecionamento recusado\", headers, fp)\n        pedido = urllib.request.Request(absoluto, method=\"GET\")\n        mesmo = (novo.hostname or \"\").lower() == (origem.hostname or \"\").lower()\n        if mesmo:\n            for chave, valor in req.header_items():\n                if chave.lower() not in (\"content-length\", \"content-type\"):\n                    pedido.add_header(chave, valor)\n        else:\n            pedido.add_header(\"User-Agent\", \"assessor-pro\")\n        return pedido\n\nop = urllib.request.build_opener(R)\ntry:\n    with op.open(req, timeout=60) as resp:\n        data = resp.read()\nexcept urllib.error.HTTPError as e:\n    if e.code in (401, 404) and not tok:\n        escrever(SEM_AUTH.format(codigo=e.code))\n    elif e.code:\n        escrever(FALHA_HTTP.format(codigo=e.code))\n    else:\n        escrever(FALHA)\n    sys.exit(1)\nexcept Exception:\n    escrever(FALHA)\n    sys.exit(1)\nif not data:\n    escrever(FALHA)\n    sys.exit(1)\nfd, path = tempfile.mkstemp(suffix=\".py\")\nos.close(fd)\nrc = 1\ntry:\n    with open(path, \"wb\") as arquivo:\n        arquivo.write(data)\n    rc = subprocess.run([sys.executable, path, modo, \"--raw\", raw, \"--saida\", saida, *extra]).returncode\nfinally:\n    os.remove(path)\nsys.exit(rc)\n")' https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable assessor /workspace/assessor/assessor.py`. Se falhar, pare e avise. Não use a cópia do disco.
4. Se o pedido inclui texto, antes de abrir o WhatsApp, no Shell: `A copiar <caminho>`. Só `copiado` segue. `falhou: arquivo não encontrado`: responda isso. `vazio`: responda `falhou: vazio`. Qualquer outra saída: responda a linha `falhou: …` do script. Se não veio `copiado`, não abra o WhatsApp e não chame o subagente.
5. Faça as conferências do core: contato único, arquivo existe e não está vazio, e nome no arquivo/texto vs destinatário. Falhou alguma: `falhou: <motivo>` ao bot, sem enviar. Exceção: se o pedido manda para o chat "você"/"(você)", esse é o destinatário autorizado. O nome do cliente dentro da mensagem ou do arquivo não muda o destino e não faz esta conferência falhar. Não abra o cliente por causa desse nome.

## Travas
Valem imediatamente antes de cada envio. PDF e texto são envios separados. A olhada na abertura não substitui estas.

1. **Destinatário.** Antes de anexar e antes de apertar enviar, leia o topo de novo. Tem que ser o destinatário autorizado: nome ou telefone do pedido; no teste, "Você" ou "(você)". Parecido, parcial, grupo ou outro contato não conta. Divergência ou dúvida: não anexe, não envie, não mande a outra parte e não tente de novo. Feche a conversa. `falhou: topo é <o que está no topo>, não <destinatário autorizado>`.
2. **Texto.** A caixa não mostra o texto longo inteiro. Isso não é falha de colagem e não se resolve olhando a tela. A prova é só a saída de `conferir-caixa`.
   1. Shell: `A copiar <caminho>` de novo, imediatamente antes de colar. Sem `copiado`, não cole e não digite. `vazio` → responda `falhou: vazio`; outra linha `falhou: …` → responda essa linha. Se o PDF já saiu, diga isso no retorno. Sem retry.
   2. Subagente: foque a caixa de mensagem e aperte Ctrl+V.
   3. Shell, só depois desse Ctrl+V: `A marcar`. Só `marcado` segue. Isso tira da área de transferência o texto do `copiar`: se o Ctrl+C do próximo passo não acontecer, a conferência lê a marca e não bate.
   4. Subagente: dentro da caixa, Ctrl+A e depois Ctrl+C. Isso põe na área de transferência o que a caixa tem.
   5. Shell, só depois desse Ctrl+C: `A conferir-caixa <caminho>`.
   6. A saída `bate` (exit 0) é a única prova. Aí o subagente aperta Enter.
   7. `nao bate` ou qualquer erro de `marcar` ou `conferir-caixa`: o subagente limpa a caixa (Ctrl+A e apaga, sem Enter). Responda `falhou: texto na caixa incompleto`. Não envie o que vem depois, não repita o que já saiu e não tente de novo.

## Proibido
- Digitar o texto, inteiro ou letra por letra.
- Abrir o `.txt` no navegador (`file://`, localhost ou qualquer aba).
- Concluir pela tela, pelo scroll ou por um trecho visível que o texto está completo ou incompleto.

## Envio
1. No WhatsApp Web, abra a conversa seguindo "Abrir e fechar conversas" do core: pelo telefone use `https://web.whatsapp.com/send?phone=<só dígitos com DDI>`; pelo nome, só um único resultado com o nome exato. Chat "você"/"(você)" = mensagem para si mesmo. No teste, abra só esse chat.
2. Confira o topo ao abrir. Se não for o destinatário autorizado, saia sem digitar e sem anexar: `falhou`.
3. **Só texto**: trava de destinatário; trava de texto (Shell `copiar`, subagente Ctrl+V, Shell `marcar`, subagente Ctrl+A e Ctrl+C, Shell `conferir-caixa`); só com `bate`, Enter.
4. **Só arquivo**: trava de destinatário; clipe/"+" → Documento → selecione o arquivo → confira o nome → sem legenda → envie. Se o topo na prévia não for o destinatário autorizado, cancele sem enviar.
5. **Texto e arquivo**: duas mensagens, nesta ordem. (a) Trava de destinatário e envie o arquivo como Documento, sem legenda. Se a trava falhar, pare: não anexe e não envie o texto. (b) Trava de destinatário de novo e a trava de texto no mesmo caminho. Sem `bate`: limpe a caixa, não envie o texto e não reenvie o arquivo.
6. Cada pedido é atendido uma vez. Pacote pela metade não segue e não tem retry automático. `falhou` diz o que saiu e o que não saiu.

## Conferir e reportar
1. Espere cada mensagem que saiu deixar o relógio: ✓ enviado, ✓✓ entregue, ✓✓ azul lido. Não marque como enviada uma parte que você não viu sair.
2. Feche a conversa (`Esc` ou voltar à lista).
3. Responda ao bot que pediu (`SendToAgent`, `priority: true`).
   - Só texto ou só arquivo: `enviado | <destinatário> | <HH:MM> | <tiques>` ou `falhou: <motivo>`.
   - Texto e arquivo: `enviado | <destinatário> | <HH:MM> | pdf <tiques> | texto <tiques>` só se os dois saíram no chat autorizado. Senão `falhou: <motivo> | pdf enviado|não enviado | texto enviado|não enviado`.

#!/usr/bin/env python3
"""Baixa arquivo da branch stable.

O token de leitura fica só na variável de ambiente GITHUB_TOKEN_BOTS.
Ele sai apenas no cabeçalho Authorization do host permitido.
Não entra na URL, no argumento, na mensagem de erro nem em arquivo.

Sem a variável, tenta sem autenticação (o repositório público responde).
HTTP 401 ou 404 sem token: a mensagem pede para definir GITHUB_TOKEN_BOTS.
"""
import argparse
import os
import re
import shlex
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request

RAW = "https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable"
AGENTE = "assessor-pro"
VAR_TOKEN = "GITHUB_TOKEN_BOTS"

SAIDA_ASSESSOR = "/workspace/assessor/assessor.py"
SAIDA_CLIENTE = "/workspace/assessor/cliente.py"
SAIDA_DISCURSO = "/workspace/assessor/discurso.md"

SCRIPT_NOVO = "bots/assessor/envio/skills/assessor-preparar-envio/scripts/assessor.py"
SCRIPT_ANTIGO = "plugins/assessor-envio/skills/assessor-preparar-envio/scripts/assessor.py"
MIN_NOVO = "bots/assessor/envio/skills/assessor-preparar-envio/scripts/versao-minima"
MIN_ANTIGO = "plugins/assessor-envio/skills/assessor-preparar-envio/scripts/versao-minima"
CLIENTE_NOVO = "bots/assessor/envio/skills/assessor-ajustar-cliente/scripts/cliente.py"
CLIENTE_ANTIGO = "plugins/assessor-envio/skills/assessor-ajustar-cliente/scripts/cliente.py"
DISCURSO = "discurso/discurso-macro.md"

SKILLS_ASSESSOR = frozenset({
    "assessor-enviar-relatorio",
    "assessor-envio-core",
    "assessor-envio-teste",
    "assessor-preparar-envio",
    "assessor-resumo-ultimo-envio",
    "assessor-zap-enviar",
})
SKILLS_CLIENTE = frozenset({"assessor-ajustar-cliente"})
SKILLS_DISCURSO = frozenset({"assessor-preparar-envio"})

MSG_SEM_AUTH = (
    "Não consegui baixar sem autenticação (HTTP {codigo}). "
    "Defina a variável de ambiente GITHUB_TOKEN_BOTS com um token de leitura do GitHub e tente de novo. "
    "Pare e não use a cópia do disco."
)
MSG_COM_TOKEN = (
    "Falha ao baixar (HTTP {codigo}) com GITHUB_TOKEN_BOTS definido. "
    "Confira se o token tem leitura deste repositório. "
    "Pare e não use a cópia do disco."
)
MSG_FALHA_HTTP = "Falha ao baixar (HTTP {codigo}). Pare e não use a cópia do disco."
MSG_FALHA = "Falha ao baixar. Pare e não use a cópia do disco."
MSG_VERSAO = "Falha ao baixar o assessor.py (exige v{minima} ou maior). Pare e não use a cópia do disco."
MSG_PREFIXO = "Falha ao baixar: a primeira linha de comentário não confere. Pare e não use a cópia do disco."
MSG_TOKEN_INVALIDO = "GITHUB_TOKEN_BOTS inválido. Pare e não use a cópia do disco."

# Programa embutido no comando da skill. Baixa este arquivo e executa o CLI.
# Não pode ter aspas simples nem crase: o comando vai entre aspas simples do shell.
BOOTSTRAP_TEMPLATE = """
import os, sys, tempfile, urllib.request, urllib.error, subprocess, urllib.parse
raw, modo, saida = sys.argv[1], sys.argv[2], sys.argv[3]
extra = sys.argv[4:]
SEM_AUTH = @@SEM@@
FALHA = @@FALHA@@
FALHA_HTTP = @@FALHA_HTTP@@
INVALIDO = @@INVALIDO@@

def host_ok(scheme, host):
    host = (host or "").lower()
    return (scheme == "https" and host == "raw.githubusercontent.com") or (scheme == "http" and host in ("127.0.0.1", "localhost"))

def escrever(msg):
    tok = os.environ.get("GITHUB_TOKEN_BOTS", "")
    if tok:
        msg = msg.replace(tok, "[redigido]")
    sys.stdout.write(msg + chr(10))

partes = urllib.parse.urlsplit(raw)
tok = os.environ.get("GITHUB_TOKEN_BOTS", "")
if not host_ok(partes.scheme, partes.hostname):
    escrever(FALHA)
    sys.exit(1)
if tok and (chr(13) in tok or chr(10) in tok):
    escrever(INVALIDO)
    sys.exit(1)
req = urllib.request.Request(raw.rstrip("/") + "/comum/baixar.py", method="GET", headers={"User-Agent": "assessor-pro"})
if tok:
    req.add_header("Authorization", "Bearer " + tok)

class R(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        absoluto = urllib.parse.urljoin(req.full_url, newurl)
        novo = urllib.parse.urlsplit(absoluto)
        origem = urllib.parse.urlsplit(req.full_url)
        if code not in (301, 302, 303, 307, 308) or not host_ok(novo.scheme, novo.hostname):
            raise urllib.error.HTTPError(req.full_url, code, "redirecionamento recusado", headers, fp)
        pedido = urllib.request.Request(absoluto, method="GET")
        mesmo = (novo.hostname or "").lower() == (origem.hostname or "").lower()
        if mesmo:
            for chave, valor in req.header_items():
                if chave.lower() not in ("content-length", "content-type"):
                    pedido.add_header(chave, valor)
        else:
            pedido.add_header("User-Agent", "assessor-pro")
        return pedido

op = urllib.request.build_opener(R)
try:
    with op.open(req, timeout=60) as resp:
        data = resp.read()
except urllib.error.HTTPError as e:
    if e.code in (401, 404) and not tok:
        escrever(SEM_AUTH.format(codigo=e.code))
    elif e.code:
        escrever(FALHA_HTTP.format(codigo=e.code))
    else:
        escrever(FALHA)
    sys.exit(1)
except Exception:
    escrever(FALHA)
    sys.exit(1)
if not data:
    escrever(FALHA)
    sys.exit(1)
fd, path = tempfile.mkstemp(suffix=".py")
os.close(fd)
rc = 1
try:
    with open(path, "wb") as arquivo:
        arquivo.write(data)
    rc = subprocess.run([sys.executable, path, modo, "--raw", raw, "--saida", saida, *extra]).returncode
finally:
    os.remove(path)
sys.exit(rc)
"""


class Falha(Exception):
    def __init__(self, codigo, msg):
        super().__init__(msg)
        self.codigo = codigo
        self.msg = msg


def _sem_segredo(msg):
    tok = os.environ.get(VAR_TOKEN, "")
    if tok:
        msg = msg.replace(tok, "[redigido]")
    return msg


def token_ou_falha():
    """Token limpo, string vazia se não houver, None se o valor não pode ir num cabeçalho."""
    tok = os.environ.get(VAR_TOKEN, "")
    if tok and any(c in tok for c in "\r\n\x00"):
        return None
    return tok


def morrer(msg):
    sys.stdout.write(_sem_segredo(msg).rstrip() + "\n")
    raise SystemExit(1)


def _host_permitido(scheme, host):
    host = (host or "").lower()
    if scheme == "https" and host == "raw.githubusercontent.com":
        return True
    if scheme == "http" and host in ("127.0.0.1", "localhost"):
        return True
    return False


class _Redirect(urllib.request.HTTPRedirectHandler):
    """Segue redirecionamento só no mesmo host permitido. Não manda o token para outro host."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        absoluto = urllib.parse.urljoin(req.full_url, newurl)
        novo = urllib.parse.urlsplit(absoluto)
        origem = urllib.parse.urlsplit(req.full_url)
        if code not in (301, 302, 303, 307, 308) or not _host_permitido(novo.scheme, novo.hostname):
            raise urllib.error.HTTPError(req.full_url, code, "redirecionamento recusado", headers, fp)
        pedido = urllib.request.Request(absoluto, method="GET")
        mesmo = (novo.hostname or "").lower() == (origem.hostname or "").lower()
        if mesmo:
            for chave, valor in req.header_items():
                if chave.lower() not in ("content-length", "content-type"):
                    pedido.add_header(chave, valor)
        else:
            pedido.add_header("User-Agent", AGENTE)
        return pedido


def _opener():
    return urllib.request.build_opener(_Redirect)


def obter(url):
    partes = urllib.parse.urlsplit(url)
    if not _host_permitido(partes.scheme, partes.hostname):
        raise Falha(0, MSG_FALHA)
    tok = token_ou_falha()
    if tok is None:
        raise Falha(0, MSG_TOKEN_INVALIDO)
    if tok and tok in url:
        raise Falha(0, MSG_FALHA)
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": AGENTE})
    if tok:
        req.add_header("Authorization", "Bearer " + tok)
    try:
        with _opener().open(req, timeout=60) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        raise Falha(e.code, "") from None
    except Exception:
        raise Falha(0, MSG_FALHA) from None


def resumir(erros):
    if not erros:
        return Falha(0, MSG_FALHA)
    if any(e.msg == MSG_TOKEN_INVALIDO for e in erros):
        return Falha(0, MSG_TOKEN_INVALIDO)
    ultimo = erros[-1].codigo
    tok = token_ou_falha()
    if tok is None:
        return Falha(0, MSG_TOKEN_INVALIDO)
    so_auth = all(e.codigo in (401, 404) for e in erros)
    if not tok and so_auth:
        return Falha(ultimo, MSG_SEM_AUTH.format(codigo=ultimo))
    if tok and so_auth:
        return Falha(ultimo, MSG_COM_TOKEN.format(codigo=ultimo))
    if ultimo:
        return Falha(ultimo, MSG_FALHA_HTTP.format(codigo=ultimo))
    return Falha(0, MSG_FALHA)


def primeiro(raw, rels):
    erros = []
    for rel in rels:
        if not rel:
            continue
        url = raw.rstrip("/") + "/" + rel.lstrip("/")
        try:
            return obter(url)
        except Falha as e:
            erros.append(e)
            if e.codigo not in (401, 404):
                break
    raise resumir(erros)


def gravar_atomico(dest, data):
    caminho = os.fspath(dest)
    pasta = os.path.dirname(caminho) or "."
    os.makedirs(pasta, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".baixar-", dir=pasta)
    try:
        os.write(fd, data)
        os.close(fd)
        fd = None
        os.replace(tmp, caminho)
        tmp = None
    finally:
        if fd is not None:
            os.close(fd)
        if tmp is not None:
            try:
                os.remove(tmp)
            except OSError:
                pass


def _baixar_um(raw, saida, rels, prefixo=""):
    try:
        data = primeiro(raw, rels)
    except Falha as e:
        morrer(e.msg or MSG_FALHA)
    if not data:
        morrer(MSG_FALHA)
    if prefixo and not _prefixo_ok(data, prefixo):
        morrer(MSG_PREFIXO)
    gravar_atomico(saida, data)


def _prefixo_ok(data, prefixo):
    """A 1ª linha de comentário (a shebang não conta) começa com o prefixo."""
    alvo = prefixo.encode("utf-8")
    for linha in data.split(b"\n"):
        if not linha.startswith(b"#"):
            continue
        if linha.startswith(b"#!"):
            continue
        return linha.startswith(alvo)
    return False


def cmd_assessor(raw, saida):
    try:
        minimo_b = primeiro(raw, [MIN_NOVO, MIN_ANTIGO])
    except Falha as e:
        morrer(e.msg or MSG_FALHA)
    texto = minimo_b.decode("utf-8", "replace").strip()
    if not texto.isdigit() or int(texto) < 1:
        morrer(MSG_VERSAO.format(minima="?"))
    minima = int(texto)
    try:
        corpo = primeiro(raw, [SCRIPT_NOVO, SCRIPT_ANTIGO])
    except Falha as e:
        morrer(e.msg or MSG_VERSAO.format(minima=minima))
    achado = re.search(br"(?m)^# assessor\.py v([0-9]+)", corpo or b"")
    if not corpo or not achado or int(achado.group(1)) < minima:
        morrer(MSG_VERSAO.format(minima=minima))
    gravar_atomico(saida, corpo)


def cmd_arquivo(raw, saida, novo, antigo="", prefixo=""):
    rels = [novo] + ([antigo] if antigo else [])
    _baixar_um(raw, saida, rels, prefixo)


def cmd_ponteiro(raw, saida, novo, antigo):
    _baixar_um(raw, saida, [novo, antigo])


def _py_string(texto):
    partes = []
    for ch in texto:
        o = ord(ch)
        if ch == '"':
            partes.append('\\"')
        elif 32 <= o < 127 and ch != "\\":
            partes.append(ch)
        else:
            partes.append("\\u%04x" % o)
    return '"' + "".join(partes) + '"'


def bootstrap_source():
    src = BOOTSTRAP_TEMPLATE
    src = src.replace("@@SEM@@", _py_string(MSG_SEM_AUTH))
    src = src.replace("@@FALHA@@", _py_string(MSG_FALHA))
    src = src.replace("@@FALHA_HTTP@@", _py_string(MSG_FALHA_HTTP))
    src = src.replace("@@INVALIDO@@", _py_string(MSG_TOKEN_INVALIDO))
    if "'" in src or "`" in src:
        raise RuntimeError("bootstrap com aspas simples ou crase")
    if not src.isascii():
        raise RuntimeError("bootstrap precisa ser ASCII")
    return src.strip() + "\n"


def _shell_exec(src):
    esc = src.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'exec("{esc}")'


def comando(modo, saida, *extra):
    corpo = _shell_exec(bootstrap_source())
    args = [RAW, modo, saida, *extra]
    # Sem "--": o python3 -c coloca esse separador em sys.argv e o raw deixa de ser a URL.
    return "python3 -c '" + corpo + "' " + " ".join(shlex.quote(a) for a in args)


def comando_assessor():
    return comando("assessor", SAIDA_ASSESSOR)


def comando_cliente():
    return comando(
        "arquivo",
        SAIDA_CLIENTE,
        "--novo",
        CLIENTE_NOVO,
        "--antigo",
        CLIENTE_ANTIGO,
        "--prefixo",
        "# cliente.py v",
    )


def comando_discurso():
    return comando("arquivo", SAIDA_DISCURSO, "--novo", DISCURSO)


def comando_ponteiro(saida, novo, antigo):
    return comando("ponteiro", saida, "--novo", novo, "--antigo", antigo)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Baixa arquivo da branch stable")
    sub = parser.add_subparsers(dest="cmd", required=True)

    assessor = sub.add_parser("assessor")
    assessor.add_argument("--raw", required=True)
    assessor.add_argument("--saida", required=True)

    arquivo = sub.add_parser("arquivo")
    arquivo.add_argument("--raw", required=True)
    arquivo.add_argument("--saida", required=True)
    arquivo.add_argument("--novo", required=True)
    arquivo.add_argument("--antigo", default="")
    arquivo.add_argument("--prefixo", default="")

    ponteiro = sub.add_parser("ponteiro")
    ponteiro.add_argument("--raw", required=True)
    ponteiro.add_argument("--saida", required=True)
    ponteiro.add_argument("--novo", required=True)
    ponteiro.add_argument("--antigo", required=True)

    args = parser.parse_args(argv)
    if args.cmd == "assessor":
        cmd_assessor(args.raw, args.saida)
    elif args.cmd == "arquivo":
        cmd_arquivo(args.raw, args.saida, args.novo, args.antigo, args.prefixo)
    else:
        cmd_ponteiro(args.raw, args.saida, args.novo, args.antigo)


if __name__ == "__main__":
    main()

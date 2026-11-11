"""Download do assessor.py: temporário, versão mínima num lugar só, sem cópia velha.

O mesmo comando está em toda skill que baixa o script. Ele baixa comum/baixar.py,
tenta o caminho novo e cai no antigo, e só substitui o arquivo de trabalho se o
download deu certo e a 1ª linha de versão é >= a mínima em versao-minima.
Falha (URL quebrada ou v6) para e deixa o disco quieto.

O token, se existir, vai só no cabeçalho Authorization. Sem token, 401/404
explica que falta GITHUB_TOKEN_BOTS.
"""
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from comum.baixar import RAW, SKILLS_ASSESSOR, comando_assessor  # noqa: E402

FONTE = ROOT / "bots/assessor"
SCRIPT = FONTE / "envio/skills/assessor-preparar-envio/scripts/assessor.py"
MINIMA = FONTE / "envio/skills/assessor-preparar-envio/scripts/versao-minima"
NOVO = "/bots/assessor/envio/skills/assessor-preparar-envio/scripts"
ANTIGO = "/plugins/assessor-envio/skills/assessor-preparar-envio/scripts"
ESPERADAS = SKILLS_ASSESSOR


def skills():
    return sorted(FONTE.glob("*/skills/*/SKILL.md")) + sorted((ROOT / "plugins").glob("*/skills/*/SKILL.md"))


def comando():
    esperado = comando_assessor()
    achados = {}
    for path in skills():
        texto = path.read_text(encoding="utf-8")
        if esperado in texto:
            achados.setdefault(path.parent.name, []).append(texto.count(esperado))
    assert set(achados) == set(ESPERADAS), sorted(achados)
    for nome, vezes in achados.items():
        assert vezes == [1, 1], (nome, vezes)
    assert esperado.count(RAW) == 1
    assert esperado.count("/workspace/assessor/assessor.py") == 1
    assert "comum/baixar.py" in esperado
    assert "GITHUB_TOKEN_BOTS" in esperado
    assert "-o /workspace/assessor/assessor.py" not in esperado
    assert "v6" not in esperado and "v7" not in esperado
    assert esperado.isascii()
    assert "\n" not in esperado
    return esperado


def versao_do_script():
    for linha in SCRIPT.read_text(encoding="utf-8").splitlines():
        if linha.startswith("# assessor.py v"):
            return int(linha.split()[2][1:])
    raise AssertionError("sem linha de versão no assessor.py")


def test_comando_igual_e_minima_num_lugar_so():
    cmd = comando()
    minima = MINIMA.read_text(encoding="utf-8")
    assert minima.strip() == "7" and minima.endswith("\n") and "\n" not in minima.strip()
    assert versao_do_script() >= int(minima.strip())
    for path in skills():
        texto = path.read_text(encoding="utf-8")
        assert "assessor.py -o /workspace/assessor/assessor.py" not in texto
        assert "-o /workspace/assessor/assessor.py" not in texto
        assert "curl -fsSL https://raw.githubusercontent.com" not in texto
    assert cmd.startswith("python3 -c ")
    assert "Bearer" in cmd


class _Handler(BaseHTTPRequestHandler):
    rotas = {}
    redirects = {}
    exigido = None
    vistos = []

    def do_GET(self):
        auth = self.headers.get("Authorization")
        if self.exigido is not None and auth != f"Bearer {self.exigido}":
            self.vistos.append((self.path, auth, 401))
            self.send_response(401)
            self.end_headers()
            return
        if self.path in self.redirects:
            self.vistos.append((self.path, auth, 302))
            self.send_response(302)
            self.send_header("Location", self.redirects[self.path])
            self.end_headers()
            return
        item = self.rotas.get(self.path)
        if item is None:
            self.vistos.append((self.path, auth, 404))
            self.send_response(404)
            self.end_headers()
            return
        self.vistos.append((self.path, auth, 200))
        self.send_response(200)
        self.send_header("Content-Length", str(len(item)))
        self.end_headers()
        self.wfile.write(item)

    def log_message(self, fmt, *args):
        pass


def _servir():
    srv = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def _rodar(cmd, dest, rotas, token=None, exigido=None, redirects=None, incluir_baixar=True):
    rotas = dict(rotas)
    if incluir_baixar:
        rotas.setdefault("/comum/baixar.py", (ROOT / "comum" / "baixar.py").read_bytes())
    _Handler.rotas = rotas
    _Handler.redirects = dict(redirects or {})
    _Handler.exigido = exigido
    _Handler.vistos = []
    srv = _servir()
    try:
        porta = srv.server_address[1]
        local = f"http://127.0.0.1:{porta}"
        c = cmd.replace(RAW, local).replace("/workspace/assessor", str(dest))
        tmp = dest.parent / "tmp"
        tmp.mkdir(exist_ok=True)
        env = {"PATH": "/usr/bin:/bin", "TMPDIR": str(tmp), "LC_ALL": "C", "LANG": "C"}
        if token is not None:
            env["GITHUB_TOKEN_BOTS"] = token
        r = subprocess.run(["bash", "-c", c], capture_output=True, text=True, env=env)
        sobras = list(tmp.iterdir())
        return r, sobras, list(_Handler.vistos)
    finally:
        srv.shutdown()


def _preparar():
    import tempfile
    dest = Path(tempfile.mkdtemp()) / "assessor"
    dest.mkdir()
    sentinela = b"SENTINELA copia antiga\n"
    (dest / "assessor.py").write_bytes(sentinela)
    return dest, sentinela


def _antigo(minima, corpo):
    return {
        f"{ANTIGO}/versao-minima": minima,
        f"{ANTIGO}/assessor.py": corpo,
    }


def test_download_sucesso_substitui():
    cmd = comando()
    dest, sentinela = _preparar()
    r, sobras, vistos = _rodar(cmd, dest, _antigo(MINIMA.read_bytes(), SCRIPT.read_bytes()))
    assert r.returncode == 0, r.stderr + r.stdout
    assert (dest / "assessor.py").read_bytes() == SCRIPT.read_bytes()
    assert (dest / "assessor.py").read_bytes() != sentinela
    assert sobras == []
    caminhos = [item[0] for item in vistos]
    assert caminhos.index(f"{NOVO}/assessor.py") < caminhos.index(f"{ANTIGO}/assessor.py")
    assert vistos[caminhos.index(f"{NOVO}/assessor.py")][2] == 404
    assert vistos[caminhos.index(f"{ANTIGO}/assessor.py")][2] == 200


def test_download_url_quebrada_nao_troca():
    cmd = comando()
    dest, sentinela = _preparar()
    r, sobras, _ = _rodar(cmd, dest, {f"{ANTIGO}/versao-minima": b"7\n"})
    assert r.returncode != 0
    assert (dest / "assessor.py").read_bytes() == sentinela
    assert "Pare e não use a cópia do disco." in r.stdout
    assert sobras == []


def test_download_v10_substitui():
    cmd = comando()
    dest, sentinela = _preparar()
    corpo = b"# assessor.py v10 | uso: teste\n"
    r, sobras, _ = _rodar(cmd, dest, _antigo(b"7\n", corpo))
    assert r.returncode == 0, r.stderr + r.stdout
    assert (dest / "assessor.py").read_bytes() == corpo
    assert (dest / "assessor.py").read_bytes() != sentinela
    assert sobras == []


def test_download_v6_nao_troca():
    cmd = comando()
    dest, sentinela = _preparar()
    corpo = b"# assessor.py v6 | uso: teste\n"
    assert corpo.startswith(b"# assessor.py v6")
    r, sobras, _ = _rodar(cmd, dest, _antigo(b"7\n", corpo))
    assert r.returncode != 0
    assert (dest / "assessor.py").read_bytes() == sentinela
    assert "exige v7 ou maior" in r.stdout
    assert "Pare e não use a cópia do disco." in r.stdout
    assert sobras == []


def test_download_com_token_e_erro_sem_token():
    cmd = comando()
    segredo = "segredo-de-teste"
    novo = b"# assessor.py v8 | caminho novo\n"
    dest, sentinela = _preparar()
    rotas = {
        f"{NOVO}/versao-minima": b"7\n",
        f"{NOVO}/assessor.py": novo,
        f"{ANTIGO}/versao-minima": b"7\n",
        f"{ANTIGO}/assessor.py": b"# assessor.py v8 | caminho antigo\n",
    }
    r, sobras, vistos = _rodar(cmd, dest, rotas, token=segredo, exigido=segredo)
    assert r.returncode == 0, r.stderr + r.stdout
    assert (dest / "assessor.py").read_bytes() == novo
    assert sobras == []
    assert vistos
    for caminho, auth, status in vistos:
        assert auth == "Bearer " + segredo
        assert segredo not in caminho
        assert status == 200
    assert all(segredo not in texto for texto in (r.stdout, r.stderr))
    assert segredo.encode() not in (dest / "assessor.py").read_bytes()
    assert f"{ANTIGO}/assessor.py" not in [item[0] for item in vistos]

    for codigo in (404, 401):
        dest, sentinela = _preparar()
        exigido = "outro-valor" if codigo == 401 else None
        r, sobras, vistos = _rodar(
            cmd, dest, {}, token=None, exigido=exigido, incluir_baixar=False,
        )
        assert r.returncode != 0
        assert (dest / "assessor.py").read_bytes() == sentinela
        assert f"HTTP {codigo}" in r.stdout
        assert "sem autenticação" in r.stdout
        assert "GITHUB_TOKEN_BOTS" in r.stdout
        assert "Pare e não use a cópia do disco." in r.stdout
        assert sobras == []
        assert all(item[1] in (None, "") for item in vistos)


def test_redirecionamento_fora_do_host_nao_leva_o_token():
    cmd = comando()
    segredo = "segredo-de-teste"
    dest, sentinela = _preparar()
    r, sobras, vistos = _rodar(
        cmd,
        dest,
        {f"{ANTIGO}/versao-minima": b"7\n", f"{ANTIGO}/assessor.py": SCRIPT.read_bytes()},
        token=segredo,
        exigido=segredo,
        redirects={f"{NOVO}/versao-minima": "http://example.invalid/x"},
    )
    assert r.returncode != 0
    assert (dest / "assessor.py").read_bytes() == sentinela
    assert "HTTP 302" in r.stdout
    assert segredo not in r.stdout and segredo not in r.stderr
    assert f"{ANTIGO}/versao-minima" not in [item[0] for item in vistos]
    assert sobras == []


if __name__ == "__main__":
    for nome, f in list(globals().items()):
        if nome.startswith("test_"):
            f()
            print("ok", nome)

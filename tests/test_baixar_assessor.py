"""Download do assessor.py: temporário, versão mínima num lugar só, sem cópia velha.

O mesmo comando está em toda skill que baixa o script. Ele só substitui o
arquivo de trabalho se o download deu certo e a 1ª linha de versão é >= a
mínima em versao-minima. Falha (URL quebrada ou v5) para e deixa o disco quieto.
"""
import re
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ROOT / 'plugins'
SCRIPT = PLUGINS / 'assessor-envio/skills/assessor-preparar-envio/scripts/assessor.py'
MINIMA = PLUGINS / 'assessor-envio/skills/assessor-preparar-envio/scripts/versao-minima'
BASE = 'https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/plugins/assessor-envio/skills/assessor-preparar-envio/scripts'
ESPERADAS = {
    'assessor-enviar-relatorio',
    'assessor-envio-core',
    'assessor-envio-teste',
    'assessor-preparar-envio',
    'assessor-resumo-ultimo-envio',
}


def comandos():
    achados = {}
    for path in sorted(PLUGINS.glob('*/skills/*/SKILL.md')):
        partes = re.findall(r'`(b=https://raw\.githubusercontent\.com/[^`]+)`', path.read_text(encoding='utf-8'))
        if partes:
            achados[path.parent.name] = partes
    return achados


def comando():
    achados = comandos()
    assert set(achados) == ESPERADAS, sorted(achados)
    textos = []
    for nome, partes in achados.items():
        assert partes == [partes[0]], nome
        textos.append(partes[0])
    assert len(set(textos)) == 1
    cmd = textos[0]
    assert cmd.count(BASE) == 1
    assert cmd.count('/workspace/assessor') == 2
    assert 'versao-minima' in cmd and 'mktemp' in cmd and '-o "$t"' in cmd and 'mv "$t"' in cmd
    assert '-o /workspace/assessor/assessor.py' not in cmd
    assert cmd.count('6') == 0  # a mínima não está repetida no comando
    return cmd


def versao_do_script():
    for linha in SCRIPT.read_text(encoding='utf-8').splitlines():
        if linha.startswith('# assessor.py v'):
            return int(linha.split()[2][1:])
    raise AssertionError('sem linha de versão no assessor.py')


def test_comando_igual_e_minima_num_lugar_so():
    cmd = comando()
    minima = MINIMA.read_text(encoding='utf-8')
    assert minima.strip() == '6' and minima.endswith('\n') and '\n' not in minima.strip()
    assert versao_do_script() >= int(minima.strip())
    for path in PLUGINS.glob('*/skills/*/SKILL.md'):
        texto = path.read_text(encoding='utf-8')
        assert 'assessor.py -o /workspace/assessor/assessor.py' not in texto
        assert 'começa com `# assessor.py v`' not in texto
    # o comando publicado é o que o teste executa
    assert cmd.startswith('b=' + BASE)


class _Handler(BaseHTTPRequestHandler):
    rotas = {}

    def do_GET(self):
        item = self.rotas.get(self.path)
        if item is None:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header('Content-Length', str(len(item)))
        self.end_headers()
        self.wfile.write(item)

    def log_message(self, fmt, *args):
        pass


def _servir():
    srv = ThreadingHTTPServer(('127.0.0.1', 0), _Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def _rodar(cmd, dest, rotas):
    _Handler.rotas = rotas
    srv = _servir()
    try:
        porta = srv.server_address[1]
        local = f'http://127.0.0.1:{porta}/scripts'
        c = cmd.replace(BASE, local).replace('/workspace/assessor', str(dest))
        tmp = dest.parent / 'tmp'
        tmp.mkdir()
        r = subprocess.run(['bash', '-c', c], capture_output=True, text=True, env={'PATH': '/usr/bin:/bin', 'TMPDIR': str(tmp)})
        sobras = list(tmp.iterdir())
        return r, sobras
    finally:
        srv.shutdown()


def test_download_sucesso_substitui():
    cmd = comando()
    dest, sentinela = _preparar()
    r, sobras = _rodar(cmd, dest, {
        '/scripts/versao-minima': MINIMA.read_bytes(),
        '/scripts/assessor.py': SCRIPT.read_bytes(),
    })
    assert r.returncode == 0, r.stderr + r.stdout
    assert (dest / 'assessor.py').read_bytes() == SCRIPT.read_bytes()
    assert (dest / 'assessor.py').read_bytes() != sentinela
    assert sobras == []


def test_download_url_quebrada_nao_troca():
    cmd = comando()
    dest, sentinela = _preparar()
    r, sobras = _rodar(cmd, dest, {'/scripts/versao-minima': b'6\n'})
    assert r.returncode != 0
    assert (dest / 'assessor.py').read_bytes() == sentinela
    assert 'Pare e não use a cópia do disco.' in r.stdout
    assert sobras == []


def test_download_v10_substitui():
    cmd = comando()
    dest, sentinela = _preparar()
    corpo = b'# assessor.py v10 | uso: teste\n'
    r, sobras = _rodar(cmd, dest, {
        '/scripts/versao-minima': b'6\n',
        '/scripts/assessor.py': corpo,
    })
    assert r.returncode == 0, r.stderr + r.stdout
    assert (dest / 'assessor.py').read_bytes() == corpo
    assert (dest / 'assessor.py').read_bytes() != sentinela
    assert sobras == []


def test_download_v5_nao_troca():
    cmd = comando()
    dest, sentinela = _preparar()
    corpo = b'# assessor.py v5 | uso: teste\n'
    assert corpo.startswith(b'# assessor.py v5')
    r, sobras = _rodar(cmd, dest, {
        '/scripts/versao-minima': b'6\n',
        '/scripts/assessor.py': corpo,
    })
    assert r.returncode != 0
    assert (dest / 'assessor.py').read_bytes() == sentinela
    assert 'exige v6 ou maior' in r.stdout
    assert 'Pare e não use a cópia do disco.' in r.stdout
    assert sobras == []


def _preparar():
    import tempfile
    dest = Path(tempfile.mkdtemp()) / 'assessor'
    dest.mkdir()
    sentinela = b'SENTINELA copia antiga\n'
    (dest / 'assessor.py').write_bytes(sentinela)
    return dest, sentinela


if __name__ == '__main__':
    for nome, f in list(globals().items()):
        if nome.startswith('test_'):
            f()
            print('ok', nome)

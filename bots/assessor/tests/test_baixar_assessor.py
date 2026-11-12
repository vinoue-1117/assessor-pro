"""Downloads das skills: temporário, conferência e só então o arquivo de trabalho.

assessor.py: o mesmo comando está em toda skill que baixa o script. Ele só
substitui o arquivo de trabalho se o download deu certo e a 1ª linha de versão
é >= a mínima em versao-minima. Falha (URL quebrada ou v6) para e deixa o disco
quieto. O cliente.py segue o mesmo formato, conferindo o prefixo `# cliente.py v`.
"""
import re
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

ASSESSOR = Path(__file__).resolve().parents[1]
SCRIPT = ASSESSOR / 'envio/skills/assessor-preparar-envio/scripts/assessor.py'
MINIMA = ASSESSOR / 'envio/skills/assessor-preparar-envio/scripts/versao-minima'
BASE = 'https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/bots/assessor/envio/skills/assessor-preparar-envio/scripts'
ESPERADAS = {
    'assessor-enviar-relatorio',
    'assessor-envio-core',
    'assessor-envio-teste',
    'assessor-preparar-envio',
    'assessor-resumo-ultimo-envio',
    'assessor-zap-enviar',
}


def comandos():
    achados = {}
    for path in sorted(ASSESSOR.glob('*/skills/*/SKILL.md')):
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
    assert minima.strip() == '7' and minima.endswith('\n') and '\n' not in minima.strip()
    assert versao_do_script() >= int(minima.strip())
    for path in ASSESSOR.glob('*/skills/*/SKILL.md'):
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


def _rodar(cmd, dest, rotas, base=BASE):
    if sys.platform == 'win32':
        pytest.skip('o comando de download roda no Shell do bot (Linux): no Windows o curl fica fora de /usr/bin e o caminho de destino tem barra invertida')
    _Handler.rotas = rotas
    srv = _servir()
    try:
        porta = srv.server_address[1]
        local = f'http://127.0.0.1:{porta}/scripts'
        c = cmd.replace(base, local).replace('/workspace/assessor', str(dest))
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
    r, sobras = _rodar(cmd, dest, {'/scripts/versao-minima': b'7\n'})
    assert r.returncode != 0
    assert (dest / 'assessor.py').read_bytes() == sentinela
    assert 'Pare e não use a cópia do disco.' in r.stdout
    assert sobras == []


def test_download_v10_substitui():
    cmd = comando()
    dest, sentinela = _preparar()
    corpo = b'# assessor.py v10 | uso: teste\n'
    r, sobras = _rodar(cmd, dest, {
        '/scripts/versao-minima': b'7\n',
        '/scripts/assessor.py': corpo,
    })
    assert r.returncode == 0, r.stderr + r.stdout
    assert (dest / 'assessor.py').read_bytes() == corpo
    assert (dest / 'assessor.py').read_bytes() != sentinela
    assert sobras == []


def test_download_v6_nao_troca():
    cmd = comando()
    dest, sentinela = _preparar()
    corpo = b'# assessor.py v6 | uso: teste\n'
    assert corpo.startswith(b'# assessor.py v6')
    r, sobras = _rodar(cmd, dest, {
        '/scripts/versao-minima': b'7\n',
        '/scripts/assessor.py': corpo,
    })
    assert r.returncode != 0
    assert (dest / 'assessor.py').read_bytes() == sentinela
    assert 'exige v7 ou maior' in r.stdout
    assert 'Pare e não use a cópia do disco.' in r.stdout
    assert sobras == []


def _preparar(arquivo='assessor.py'):
    import tempfile
    dest = Path(tempfile.mkdtemp()) / 'assessor'
    dest.mkdir()
    sentinela = b'SENTINELA copia antiga\n'
    (dest / arquivo).write_bytes(sentinela)
    return dest, sentinela


CLIENTE = ASSESSOR / 'envio/skills/assessor-ajustar-cliente/scripts/cliente.py'
URL_CLIENTE = 'https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/bots/assessor/envio/skills/assessor-ajustar-cliente/scripts'


def comando_mktemp(path):
    partes = re.findall(r'`(t=\$\(mktemp\)[^`]+)`', path.read_text(encoding='utf-8'))
    assert len(partes) == 1, path
    cmd = partes[0]
    assert '-o "$t"' in cmd and 'mv "$t"' in cmd and 'Pare e não use a cópia do disco.' in cmd, path
    return cmd


def comando_cliente():
    cmd = comando_mktemp(ASSESSOR / 'envio/skills/assessor-ajustar-cliente/SKILL.md')
    assert cmd.count(URL_CLIENTE + '/cliente.py') == 1 and "grep -q '^# cliente.py v'" in cmd
    for path in ASSESSOR.glob('*/skills/*/SKILL.md'):
        assert '-o /workspace/assessor/cliente.py' not in path.read_text(encoding='utf-8'), path
    return cmd


def test_cliente_sucesso_substitui():
    dest, sentinela = _preparar('cliente.py')
    r, sobras = _rodar(comando_cliente(), dest, {'/scripts/cliente.py': CLIENTE.read_bytes()}, base=URL_CLIENTE)
    assert r.returncode == 0, r.stderr + r.stdout
    assert (dest / 'cliente.py').read_bytes() == CLIENTE.read_bytes()
    assert sobras == []


def test_cliente_url_quebrada_nao_troca():
    dest, sentinela = _preparar('cliente.py')
    r, sobras = _rodar(comando_cliente(), dest, {}, base=URL_CLIENTE)
    assert r.returncode != 0
    assert (dest / 'cliente.py').read_bytes() == sentinela
    assert 'Pare e não use a cópia do disco.' in r.stdout
    assert sobras == []


if __name__ == '__main__':
    for nome, f in list(globals().items()):
        if nome.startswith('test_'):
            f()
            print('ok', nome)

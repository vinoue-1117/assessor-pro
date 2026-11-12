"""Analista offline: mercado.py com yfinance mockado, download versionado e privacidade.

O comando de Shell do bot roda em Linux. No Windows o teste que executa o
comando e pulado: curl fora do PATH e barra invertida no destino.
"""
import contextlib
import importlib.util
import io
import json
import re
import subprocess
import sys
import threading
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
SCRIPT = RAIZ / 'skills/analista-mercado/scripts/mercado.py'
MINIMA = RAIZ / 'skills/analista-mercado/scripts/versao-minima'
BASE = 'https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/bots/analista/skills/analista-mercado/scripts'
SKILLS_COM_DOWNLOAD = {'analista-core', 'analista-mercado'}


def _carregar():
    spec = importlib.util.spec_from_file_location('mercado_analista', SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = _carregar()


class Quadro:
    """Tabela minima no lugar do DataFrame do pandas."""

    def __init__(self, colunas, linhas, indice):
        self.columns = list(colunas)
        self._linhas = [list(r) for r in linhas]
        self.index = list(indice)
        self.empty = len(self._linhas) == 0

    def copy(self):
        return Quadro(self.columns, self._linhas, self.index)

    def iterrows(self):
        for idx, vals in zip(self.index, self._linhas):
            yield idx, {c: v for c, v in zip(self.columns, vals)}


def _yf(monkeypatch, ticker_cls):
    mod = type(sys)('yfinance')
    mod.Ticker = ticker_cls
    monkeypatch.setitem(sys.modules, 'yfinance', mod)


def rodar(argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        with pytest.raises(SystemExit) as exc:
            MOD.main(argv)
    code = exc.value.code
    if code is None:
        code = 0
    bruto = buf.getvalue()
    assert 'NaN' not in bruto
    return code, json.loads(bruto), bruto


def test_normalizar_b3_eua_indice_cambio():
    assert MOD.normalizar('petr4') == 'PETR4.SA'
    assert MOD.normalizar(' PETR4 ') == 'PETR4.SA'
    assert MOD.normalizar('BOVA11') == 'BOVA11.SA'
    assert MOD.normalizar('TAEE11') == 'TAEE11.SA'
    assert MOD.normalizar('PETR4.SA') == 'PETR4.SA'
    assert MOD.normalizar('AAPL') == 'AAPL'
    assert MOD.normalizar('brk.b') == 'BRK.B'
    assert MOD.normalizar('^gspc') == '^GSPC'
    assert MOD.normalizar('^BVSP') == '^BVSP'
    assert MOD.normalizar('brl=x') == 'BRL=X'
    assert MOD.normalizar('EURUSD=X') == 'EURUSD=X'


def test_cotacao_campos_fonte_e_simbolo(monkeypatch):
    vistos = []

    class Ticker:
        def __init__(self, sym):
            vistos.append(sym)
            self.sym = sym

        def history(self, **kw):
            assert kw['auto_adjust'] is False
            assert kw['interval'] == '1d'
            if self.sym == 'PETR4.SA':
                return Quadro(
                    ['Open', 'High', 'Low', 'Close', 'Volume'],
                    [[29.0, 31.0, 28.5, 30.0, 1000], [30.0, 32.0, 29.5, 31.5, 1100]],
                    [date(2026, 11, 11), date(2026, 11, 12)],
                )
            return Quadro(
                ['Open', 'High', 'Low', 'Close', 'Volume'],
                [[10.0, 11.0, 9.0, 10.5, 5]],
                [date(2026, 11, 12)],
            )

        @property
        def info(self):
            if self.sym == 'PETR4.SA':
                return {'shortName': 'Petrobras', 'currency': 'BRL'}
            raise RuntimeError('info instavel')

        @property
        def fast_info(self):
            raise RuntimeError('fast instavel')

    _yf(monkeypatch, Ticker)
    code, data, _ = rodar(['cotacao', 'petr4', '^gspc', 'brl=x'])
    assert code == 0
    assert vistos == ['PETR4.SA', '^GSPC', 'BRL=X']
    petr = data[0]
    assert petr['ticker'] == 'PETR4'
    assert petr['ticker_yf'] == 'PETR4.SA'
    assert petr['preco'] == 31.5
    assert petr['variacao_pct'] == 5.0
    assert petr['abertura'] == 30.0
    assert petr['maxima'] == 32.0
    assert petr['minima'] == 29.5
    assert petr['volume'] == 1100
    assert petr['moeda'] == 'BRL'
    assert petr['nome'] == 'Petrobras'
    assert petr['data_pregao'] == '2026-11-12'
    assert petr['fonte'] == 'yfinance'
    assert petr['atraso_estimado_min'] == 15
    assert petr['consultado_em'].endswith('-03:00')
    assert data[1]['ticker_yf'] == '^GSPC'
    assert data[1]['preco'] == 10.5
    assert data[1]['variacao_pct'] is None
    assert data[1]['nome'] is None
    assert data[1]['moeda'] is None
    assert data[2]['ticker_yf'] == 'BRL=X'


def test_cotacao_ticker_falha(monkeypatch):
    class Ticker:
        def __init__(self, sym):
            self.sym = sym

        def history(self, **kw):
            if self.sym == 'FAIL4.SA':
                return Quadro(['Close'], [], [])
            raise RuntimeError('rede caiu')

        @property
        def info(self):
            return {}

    _yf(monkeypatch, Ticker)
    code, data, bruto = rodar(['cotacao', 'FAIL4', 'AAPL'])
    assert code != 0
    assert isinstance(data, list) and len(data) == 2
    assert data[0]['erro']
    assert data[0]['consultado_em'].endswith('-03:00')
    assert 'preco' not in data[0]
    assert 'yfinance sem dados para FAIL4.SA' in data[0]['erro']
    assert 'RuntimeError' in data[1]['erro']
    assert 'consultado_em' in data[1]
    assert 'NaN' not in bruto

    code1, um, _ = rodar(['cotacao', 'ZZZZ'])
    assert code1 != 0
    assert um[0]['erro']
    assert um[0]['consultado_em']


def test_historico_ohlcv_e_intervalo(monkeypatch):
    class Ticker:
        kwargs = None

        def __init__(self, sym):
            assert sym == 'PETR4.SA'

        def history(self, **kw):
            Ticker.kwargs = kw
            return Quadro(
                ['Open', 'High', 'Low', 'Close', 'Volume'],
                [[1.0, 2.0, 0.5, 1.5, 10], [1.5, 2.5, 1.0, None, 11]],
                [date(2026, 10, 1), date(2026, 10, 2)],
            )

    _yf(monkeypatch, Ticker)
    code, data, _ = rodar(['historico', 'PETR4', '--de', '2026-10-01', '--ate', '2026-10-15', '--intervalo', '1w'])
    assert code == 0
    assert Ticker.kwargs['interval'] == '1wk'
    assert Ticker.kwargs['start'] == '2026-10-01'
    assert Ticker.kwargs['end'] == '2026-10-16'
    assert Ticker.kwargs['auto_adjust'] is False
    assert data['ticker_yf'] == 'PETR4.SA'
    assert data['intervalo'] == '1w'
    assert data['fonte'] == 'yfinance'
    assert data['atraso_estimado_min'] == 15
    assert data['consultado_em'].endswith('-03:00')
    assert data['dados'] == [{
        'data': '2026-10-01',
        'abertura': 1.0,
        'maxima': 2.0,
        'minima': 0.5,
        'fechamento': 1.5,
        'volume': 10,
    }]

    code_i, ruim, _ = rodar(['historico', 'PETR4', '--intervalo', '5m'])
    assert code_i != 0
    assert 'intervalo inválido' in ruim['erro']
    assert ruim['consultado_em']

    code_d, data_ruim, _ = rodar(['historico', 'PETR4', '--de', '2026-13-01'])
    assert code_d != 0
    assert 'data inválida' in data_ruim['erro']


def test_historico_multiindex(monkeypatch):
    class Ticker:
        def __init__(self, sym):
            self.sym = sym

        def history(self, **kw):
            if self.sym == 'AAPL':
                cols = [('AAPL', 'Open'), ('AAPL', 'High'), ('AAPL', 'Low'), ('AAPL', 'Close'), ('AAPL', 'Volume')]
            else:
                cols = [('Open', 'VALE3.SA'), ('High', 'VALE3.SA'), ('Low', 'VALE3.SA'), ('Close', 'VALE3.SA'), ('Volume', 'VALE3.SA')]
            return Quadro(cols, [[4.0, 5.0, 3.0, 4.5, 7]], [date(2026, 11, 10)])

    _yf(monkeypatch, Ticker)
    code, aapl, _ = rodar(['historico', 'AAPL', '--de', '2026-11-01', '--ate', '2026-11-10'])
    assert code == 0
    assert aapl['dados'][0]['fechamento'] == 4.5
    assert aapl['dados'][0]['volume'] == 7
    code2, vale, _ = rodar(['historico', 'VALE3', '--de', '2026-11-01', '--ate', '2026-11-10'])
    assert code2 == 0
    assert vale['ticker_yf'] == 'VALE3.SA'
    assert vale['dados'][0]['abertura'] == 4.0
    assert vale['dados'][0]['maxima'] == 5.0
    assert vale['dados'][0]['minima'] == 3.0


def test_opcoes_eua_e_erro_b3(monkeypatch):
    chamadas = []

    class Chain:
        calls = Quadro(
            ['contractSymbol', 'strike', 'lastPrice', 'bid', 'ask', 'volume', 'impliedVolatility'],
            [
                ['C100', 100, 1.2, 1.1, 1.3, 0, 0.25],
                ['C110', 110, 0.5, 0.4, 0.6, 12, 0.30],
                ['C120', 120, 0.1, 0.1, 0.2, float('nan'), 0.40],
            ],
            [0, 1, 2],
        )
        puts = Quadro(
            ['contractSymbol', 'strike', 'lastPrice', 'bid', 'ask', 'volume', 'impliedVolatility'],
            [['P100', 100, 2.0, 1.9, 2.1, 4, 0.28]],
            [0],
        )

    class Ticker:
        options = ['2026-12-18', '2027-01-16']

        def __init__(self, sym):
            chamadas.append(sym)
            if sym.endswith('.SA'):
                raise AssertionError(sym)

        def option_chain(self, venc):
            assert venc == '2026-12-18'
            return Chain()

    _yf(monkeypatch, Ticker)
    code, data, bruto = rodar(['opcoes', 'AAPL', '--tipo', 'put'])
    assert code == 0
    assert 'NaN' not in bruto
    assert data['ticker_yf'] == 'AAPL'
    assert data['fonte'] == 'yfinance'
    assert data['atraso_estimado_min'] == 15
    assert data['vencimento'] == '2026-12-18'
    assert [o['codigo'] for o in data['opcoes']] == ['P100']
    assert data['opcoes'][0]['tipo'] == 'PUT'
    assert data['opcoes'][0]['iv_pct'] == 28.0

    code_s, filtrada, _ = rodar(['opcoes', 'AAPL', '--so-negociadas'])
    assert code_s == 0
    assert [o['codigo'] for o in filtrada['opcoes']] == ['C110', 'P100']
    assert filtrada['opcoes'][0]['volume'] == 12
    assert filtrada['opcoes'][0]['iv_pct'] == 30.0

    code_t, toda, _ = rodar(['opcoes', 'AAPL'])
    assert code_t == 0
    nan = [o for o in toda['opcoes'] if o['codigo'] == 'C120'][0]
    assert nan['volume'] is None

    code_v, venc, _ = rodar(['opcoes', 'AAPL', '--vencimento', '1999-01-01'])
    assert code_v != 0
    assert 'não existe no yfinance' in venc['erro']
    assert venc['consultado_em']

    chamadas.clear()
    code_b, b3, _ = rodar(['opcoes', 'petr4'])
    assert code_b != 0
    assert chamadas == []
    assert b3['erro'].startswith('yfinance não fornece cadeia de opções da B3 (PETR4.SA)')
    assert b3['consultado_em'].endswith('-03:00')
    assert 'preco' not in b3

    code_s2, ja, _ = rodar(['opcoes', 'PETR4.SA'])
    assert code_s2 != 0
    assert 'PETR4.SA' in ja['erro']
    assert chamadas == []


def test_subcomando_desconhecido_lista_uso():
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        with pytest.raises(SystemExit) as exc:
            MOD.main(['nao-existe'])
    assert exc.value.code != 0
    texto = err.getvalue()
    assert 'cotacao' in texto and 'historico' in texto and 'opcoes' in texto


def comandos():
    achados = {}
    for path in sorted((RAIZ / 'skills').glob('*/SKILL.md')):
        partes = re.findall(r'`(b=https://raw\.githubusercontent\.com/[^`]+)`', path.read_text(encoding='utf-8'))
        if partes:
            achados[path.parent.name] = partes
    return achados


def comando():
    achados = comandos()
    assert set(achados) == SKILLS_COM_DOWNLOAD, sorted(achados)
    textos = []
    for nome, partes in achados.items():
        assert partes == [partes[0]], nome
        textos.append(partes[0])
    assert len(set(textos)) == 1
    cmd = textos[0]
    assert cmd.count(BASE) == 1
    assert cmd.count('/workspace/analista') == 2
    assert 'versao-minima' in cmd and 'mktemp' in cmd and '-o "$t"' in cmd and 'mv "$t"' in cmd
    assert '-o /workspace/analista/mercado.py' not in cmd
    assert '^# mercado.py v' in cmd
    assert 'v${min:-?}' in cmd
    assert cmd.startswith('b=' + BASE)
    return cmd


def test_comando_download_igual_e_versao():
    cmd = comando()
    minima = MINIMA.read_text(encoding='utf-8')
    assert minima == '1\n'
    primeira = SCRIPT.read_text(encoding='utf-8').splitlines()[0]
    assert primeira == '# mercado.py v1'
    assert int(primeira.split()[2][1:]) >= int(minima.strip())
    for path in (RAIZ / 'skills').glob('*/SKILL.md'):
        texto = path.read_text(encoding='utf-8')
        assert '-o /workspace/analista/mercado.py' not in texto
        assert 'começa com `# mercado.py v`' not in texto
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


def _rodar_download(cmd, dest, rotas):
    if sys.platform == 'win32':
        pytest.skip('o comando de download roda no Shell do bot (Linux): no Windows o curl fica fora de /usr/bin e o caminho de destino tem barra invertida')
    _Handler.rotas = rotas
    srv = _servir()
    try:
        porta = srv.server_address[1]
        local = f'http://127.0.0.1:{porta}/scripts'
        c = cmd.replace(BASE, local).replace('/workspace/analista', str(dest))
        tmp = dest.parent / 'tmp'
        tmp.mkdir(exist_ok=True)
        r = subprocess.run(
            ['bash', '-c', c],
            capture_output=True,
            text=True,
            encoding='utf-8',
            env={'PATH': '/usr/bin:/bin', 'TMPDIR': str(tmp), 'LC_ALL': 'C.UTF-8'},
        )
        sobras = list(tmp.iterdir())
        return r, sobras
    finally:
        srv.shutdown()


def _preparar():
    import tempfile
    dest = Path(tempfile.mkdtemp()) / 'analista'
    dest.mkdir()
    sentinela = b'SENTINELA copia antiga\n'
    (dest / 'mercado.py').write_bytes(sentinela)
    return dest, sentinela


def test_download_sucesso_substitui():
    dest, sentinela = _preparar()
    r, sobras = _rodar_download(comando(), dest, {
        '/scripts/versao-minima': MINIMA.read_bytes(),
        '/scripts/mercado.py': SCRIPT.read_bytes(),
    })
    assert r.returncode == 0, r.stderr + r.stdout
    assert (dest / 'mercado.py').read_bytes() == SCRIPT.read_bytes()
    assert (dest / 'mercado.py').read_bytes() != sentinela
    assert sobras == []


def test_download_url_quebrada_nao_troca():
    dest, sentinela = _preparar()
    r, sobras = _rodar_download(comando(), dest, {'/scripts/versao-minima': b'1\n'})
    assert r.returncode != 0
    assert (dest / 'mercado.py').read_bytes() == sentinela
    assert 'Pare e não use a cópia do disco.' in r.stdout
    assert sobras == []


def test_download_versao_menor_nao_troca_e_maior_troca():
    dest, sentinela = _preparar()
    r, sobras = _rodar_download(comando(), dest, {
        '/scripts/versao-minima': b'1\n',
        '/scripts/mercado.py': b'# mercado.py v0\n',
    })
    assert r.returncode != 0
    assert (dest / 'mercado.py').read_bytes() == sentinela
    assert 'exige v1 ou maior' in r.stdout
    assert 'Pare e não use a cópia do disco.' in r.stdout
    assert sobras == []

    corpo = b'# mercado.py v2\n'
    r2, sobras2 = _rodar_download(comando(), dest, {
        '/scripts/versao-minima': b'1\n',
        '/scripts/mercado.py': corpo,
    })
    assert r2.returncode == 0, r2.stderr + r2.stdout
    assert (dest / 'mercado.py').read_bytes() == corpo
    assert sobras2 == []


def test_sem_referencias_proibidas_e_lf():
    proibidos = [
        'OPLAB_' + 'ACCESS_TOKEN',
        'ANTHROPIC_' + 'API_KEY',
        'llm' + '.py',
        'anthropic-' + 'offload',
        'watch' + 'list',
        'revisar_' + 'tese',
        'Lu' + 'iz',
        'Vic' + 'tor',
    ]
    for path in RAIZ.rglob('*'):
        if not path.is_file() or path.suffix == '.pyc':
            continue
        dados = path.read_bytes()
        assert b'\r' not in dados, path
        texto = dados.decode('utf-8').casefold()
        for termo in proibidos:
            assert termo.casefold() not in texto, f'{termo} em {path}'

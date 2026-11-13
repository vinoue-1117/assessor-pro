"""Analista offline: mercado.py com yfinance, Banco Central e Tesouro mockados, download versionado e privacidade.

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
SKILLS_COM_DOWNLOAD = {'analista-mercado'}


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


def test_taxa_bcb_ultimo_valor_ate_hoje(monkeypatch):
    hoje = MOD.datetime.now(MOD.TZ).date()

    def dia(n):
        return (hoje + MOD.timedelta(days=n)).strftime('%d/%m/%Y')

    # A meta Selic vem preenchida para a frente e a ordem das datas varia entre series.
    series = {
        432: [{'data': dia(20), 'valor': '99.00'}, {'data': dia(0), 'valor': '13.75'}, {'data': dia(-1), 'valor': '14.25'}],
        1178: [{'data': dia(-1), 'valor': '13.65'}, {'data': dia(-2), 'valor': '13.90'}],
        433: [{'data': dia(-40), 'valor': '0.14'}],
        13522: [{'data': dia(-40), 'valor': '4.63'}],
    }
    pedidos = []

    def baixar(codigo, de, ate):
        pedidos.append((codigo, ate))
        if codigo not in series:
            raise RuntimeError('rede caiu')
        return series[codigo]

    monkeypatch.setattr(MOD, 'baixar_sgs', baixar)
    code, data, _ = rodar(['taxa', 'selic', 'IPCA'])
    assert code == 0
    selic, ipca = data
    assert selic['meta'] == {'valor': 13.75, 'unidade': '% a.a.', 'data': hoje.isoformat(), 'serie_sgs': 432}
    assert selic['efetiva']['valor'] == 13.65
    assert selic['fonte'] == 'bcb-sgs'
    assert selic['consultado_em'].endswith('-03:00')
    assert 'atraso_estimado_min' not in selic
    assert ipca['indicador'] == 'ipca'
    assert ipca['mes']['valor'] == 0.14
    assert ipca['acumulado_12m']['valor'] == 4.63
    assert pedidos == [(432, hoje), (1178, hoje), (433, hoje), (13522, hoje)]

    code2, ruim, _ = rodar(['taxa', 'cdi', 'di'])
    assert code2 != 0
    assert 'RuntimeError' in ruim[0]['erro']
    assert 'taxa' not in ruim[0]
    assert 'indicador inválido' in ruim[1]['erro']
    assert ruim[1]['consultado_em']


def test_tesouro_data_base_mais_recente_e_filtro(monkeypatch):
    cab = 'Tipo Titulo;Data Vencimento;Data Base;Taxa Compra Manha;Taxa Venda Manha;PU Compra Manha;PU Venda Manha;PU Base Manha'
    # A data-base mais recente fica no meio: a ordem das linhas nao e garantida.
    linhas = [
        'Tesouro Prefixado;01/01/2030;09/11/2026;9,99;9,99;700,00;699,00;699,00',
        'Tesouro Prefixado;01/01/2030;10/11/2026;14,65;14,77;748,89;746,82;746,82',
        'Tesouro IPCA+;15/05/2035;10/11/2026;7,70;7,82;2100,50;2080,25;2080,25',
        'Tesouro IPCA+ com Juros Semestrais;15/08/2032;10/11/2026;7,64;7,76;4300,10;4280,00;4280,00',
        'Tesouro IPCA+;15/05/2035;06/11/2026;1,11;1,11;1,00;1,00;1,00',
    ]
    monkeypatch.setattr(MOD, 'baixar_tesouro', lambda: '\n'.join([cab, *linhas]) + '\n')

    code, data, _ = rodar(['tesouro', '--tipo', 'IPCA+'])
    assert code == 0
    assert data['data_base'] == '2026-11-10'
    assert data['fonte'] == 'tesouro-transparente'
    assert data['consultado_em'].endswith('-03:00')
    assert data['titulos'] == [
        {'titulo': 'Tesouro IPCA+', 'vencimento': '2035-05-15', 'taxa_compra': 7.7, 'taxa_venda': 7.82, 'pu_compra': 2100.5, 'pu_venda': 2080.25},
        {'titulo': 'Tesouro IPCA+ com Juros Semestrais', 'vencimento': '2032-08-15', 'taxa_compra': 7.64, 'taxa_venda': 7.76, 'pu_compra': 4300.1, 'pu_venda': 4280.0},
    ]

    code_t, todos, _ = rodar(['tesouro'])
    assert code_t == 0
    assert len(todos['titulos']) == 3

    code_f, vazio, _ = rodar(['tesouro', '--tipo', 'cambial'])
    assert code_f != 0
    assert 'Tesouro Prefixado' in vazio['erro']
    assert 'titulos' not in vazio

    monkeypatch.setattr(MOD, 'baixar_tesouro', lambda: 'Titulo;Data Base\nTesouro Selic;10/11/2026\n')
    code_c, formato, _ = rodar(['tesouro'])
    assert code_c != 0
    assert 'mudou de formato' in formato['erro']

    def caiu():
        raise RuntimeError('rede caiu')

    monkeypatch.setattr(MOD, 'baixar_tesouro', caiu)
    code_r, rede, _ = rodar(['tesouro'])
    assert code_r != 0
    assert 'RuntimeError' in rede['erro']


def test_subcomando_desconhecido_lista_uso():
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        with pytest.raises(SystemExit) as exc:
            MOD.main(['nao-existe'])
    assert exc.value.code != 0
    texto = err.getvalue()
    assert 'cotacao' in texto and 'historico' in texto and 'opcoes' in texto and 'taxa' in texto and 'tesouro' in texto


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
    assert minima == '3\n'
    primeira = SCRIPT.read_text(encoding='utf-8').splitlines()[0]
    assert primeira == '# mercado.py v3'
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


def _rodar_eval():
    spec = importlib.util.spec_from_file_location('rodar_eval_revisor', RAIZ / 'evals/revisor/rodar.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_eval_revisor_monta_um_caso_por_braco_e_rascunho(tmp_path, monkeypatch):
    rodar_eval = _rodar_eval()
    rodar_eval.montar(tmp_path, 5)
    casos = tmp_path / 'evals'
    assert sorted(p.name for p in casos.iterdir()) == ['advogado', 'advogado-limpo', 'conferente', 'conferente-limpo']
    pasta = RAIZ / 'evals/revisor'
    papeis, entradas, usados = {}, {}, set()
    for sufixo, (_, arquivo, gab) in rodar_eval.RASCUNHOS.items():
        # Cada criterio do gabarito confere um trecho que existe uma vez no rascunho dele.
        gabarito = rodar_eval.gabarito(gab)
        rascunho = (pasta / arquivo).read_text(encoding='utf-8')
        for nome, trecho in gabarito.items():
            assert nome == 'aprova' or rascunho.count(trecho) == 1, nome
        usados |= set(gabarito)
        for braco in ('advogado', 'conferente'):
            caso = casos / (braco + sufixo)
            cabeca, entradas[caso.name] = (caso / 'prompt.md').read_text(encoding='utf-8').split('## Rascunho', 1)
            assert 'runs: 5' in cabeca
            papeis[caso.name] = cabeca.split('Papel: ', 1)[1].strip()
            assert sorted(p.stem for p in (caso / 'graders').iterdir()) == sorted(gabarito)
    assert usados == {p.stem for p in (pasta / 'graders').iterdir()}
    # Os dois bracos de um rascunho recebem a mesma entrada; o rascunho sem erro nao traz nenhum erro plantado.
    assert entradas['advogado'] == entradas['conferente'] != entradas['advogado-limpo'] == entradas['conferente-limpo']
    assert '"contas"' in entradas['advogado']
    for nome, trecho in rodar_eval.gabarito('gabarito.json').items():
        assert nome.startswith('erro-') != (trecho in entradas['advogado-limpo']), nome
    # O braco A e o papel que a skill passa ao revisor, lido da propria skill.
    assert f"- o papel: {papeis['advogado']}\n" in (RAIZ / 'skills/analista-tese/SKILL.md').read_text(encoding='utf-8')
    assert papeis['conferente'].startswith('conferente factual')
    assert papeis['advogado-limpo'] == papeis['advogado'] and papeis['conferente-limpo'] == papeis['conferente']
    # Papel trocado na skill: o eval para, em vez de rodar o braco `advogado` com outro papel.
    trocada = tmp_path / 'SKILL.md'
    trocada.write_text('- o papel: conferente factual. Conferir cada numero.\n', encoding='utf-8')
    monkeypatch.setattr(rodar_eval, 'SKILL', trocada)
    with pytest.raises(SystemExit, match='advogado do diabo'):
        rodar_eval.bracos()


def test_eval_revisor_relatorio_de_entrada_marca_o_gabarito(tmp_path):
    rodar_eval = _rodar_eval()
    pagina = rodar_eval.relatorio_entrada(tmp_path, 5).read_text(encoding='utf-8')
    nomes = [n for _, _, gab in rodar_eval.RASCUNHOS.values() for n in rodar_eval.gabarito(gab)]
    for tipo in ('erro', 'correta'):
        assert pagina.count(f'<mark class="{tipo}" title=') == sum(n.startswith(tipo) for n in nomes) > 0
    assert rodar_eval.ler('papel-conferente.md') in pagina


def test_eval_revisor_soma_a_regua_so_de_execucao_julgada_e_com_veredito(capsys):
    rodar_eval = _rodar_eval()
    # Vale o veredito declarado: "resultado" no corpo da resposta ou em cabecalho de tabela nao conta.
    refazer = 'O resultado da conta diverge do JSON.\n\n# Veredito: `refazer`'
    fragil = '| Item | Resultado |\n| taxa | confere |\n\n## Veredito\n\n**frágil**'

    def execucao(resposta, criterios, erro=None):
        return {'error': erro, 'graders': [{'name': n, 'passed': p, 'evidence': resposta} for n, p in criterios.items()]}

    soma = rodar_eval.somar({'cases': [
        {'name': 'advogado', 'arms': {'with': [
            execucao(refazer, {'erro-a': True, 'erro-b': False, 'correta-a': False, 'correta-b': True}),
            execucao('', {}, erro='timeout'),
            execucao(refazer, {}),
            execucao(refazer, {'erro-a': None, 'correta-a': True}),
            execucao('O resultado da conta', {'erro-a': False, 'correta-a': True}),
        ]}},
        {'name': 'advogado-limpo', 'arms': {'with': [execucao(fragil, {'aprova': False, 'correta-a': True})]}},
    ]})
    assert soma == {
        'advogado': [{'erros': 1, 'de_erros': 2, 'contestadas': 1, 'de_corretas': 2, 'aprovou': None,
                      'resposta': refazer, 'veredito': 'refazer'}],
        'advogado-limpo': [{'erros': 0, 'de_erros': 0, 'contestadas': 0, 'de_corretas': 1, 'aprovou': False,
                            'resposta': fragil, 'veredito': 'frágil'}],
    }
    fora = capsys.readouterr().err
    for motivo in ('erro: timeout', 'nenhum criterio julgado', 'criterio sem julgamento: erro-a', 'resposta sem veredito'):
        assert motivo in fora, motivo


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

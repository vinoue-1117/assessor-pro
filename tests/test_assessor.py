"""Checagem do assessor.py sem PDFs reais: planilha, telefone, discurso e estado do lote.

Roda com `python tests/test_assessor.py` (ou pytest). A leitura dos PDFs fica no teste manual com um lote real.
"""
import contextlib, csv, io, os, sys, tempfile, zipfile
from pathlib import Path

BASE = Path(tempfile.mkdtemp())
os.environ['ASSESSOR_BASE'] = str(BASE)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'plugins/assessor-envio/skills/assessor-preparar-envio/scripts'))
import assessor  # noqa: E402


def rodar(f, *args):
    """(saída, código de saída) de um subcomando."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        try:
            f(*args)
            cod = 0
        except SystemExit as e:
            cod = e.code
    return out.getvalue(), cod


def test_planilha_baguncada_csv():
    p = BASE / 'clientes.csv'
    p.write_text('Clientes do escritório\n\nConta XP;Celular;Nome do Cliente\n123;11 98765-4321;MARIA SILVA\n;;\n', encoding='utf-8')
    assert assessor.ler_planilha(p) == [{'conta_xp': '123', 'telefone': '11 98765-4321', 'nome': 'MARIA SILVA', 'apelido': ''}]


def test_importar_limpa_para_o_cliente_py():
    import subprocess
    (BASE / 'clientes.xlsx').write_bytes(b'versao anterior')  # ativa de versão anterior vira backup
    p = BASE / 'entrada.csv'
    p.write_text('Minha carteira\nConta XP;Celular;Nome do Cliente;Como chamar\n'
                 '00123;11 98765-4321;  Maria   Silva ;Mari\n;11 90000-0000;Sem Conta;\n456;98765-4321;JOSE;\n', encoding='utf-8')
    saida, cod = rodar(assessor.importar, p)
    assert cod == 0 and 'IMPORTADO 2 clientes' in saida and '1 linhas sem conta' in saida and '456' in saida
    ativa = BASE / 'clientes.csv'
    assert ativa.read_text(encoding='utf-8').splitlines() == [
        'conta_xp,telefone,nome,apelido', '00123,+5511987654321,Maria Silva,Mari', '456,98765-4321,JOSE,']
    assert not (BASE / 'clientes.xlsx').exists() and list(BASE.glob('clientes.bak-*.xlsx'))
    # o cliente.py (leitor estrito) trabalha sobre a planilha limpa
    cli = Path(assessor.__file__).parents[2] / 'assessor-ajustar-cliente/scripts/cliente.py'
    r = subprocess.run([sys.executable, str(cli), str(ativa), 'set', '456', 'telefone', '21 99876-5432'], capture_output=True, text=True, encoding='utf-8')
    assert r.returncode == 0, r.stderr
    assert '456,+5521998765432,JOSE,' in ativa.read_text(encoding='utf-8')


def test_planilha_sem_coluna_obrigatoria_explica():
    p = BASE / 'ruim.csv'
    p.write_text('conta,nome\n1,Ana\n', encoding='utf-8')
    msg, cod = rodar(assessor.ler_planilha, p)
    assert cod and 'telefone' in str(cod)


def test_xlsx_le_a_primeira_aba_da_pasta():
    p = BASE / 'abas.xlsx'
    folha = lambda v: f'<worksheet><sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>conta</t></is></c><c r="B1" t="inlineStr"><is><t>telefone</t></is></c><c r="C1" t="inlineStr"><is><t>nome</t></is></c></row><row r="2"><c r="A2"><v>{v}</v></c><c r="B2"><v>5511987654321</v></c><c r="C2" t="inlineStr"><is><t>Ana</t></is></c></row></sheetData></worksheet>'
    with zipfile.ZipFile(p, 'w') as z:
        z.writestr('xl/workbook.xml', '<workbook><sheets><sheet name="Clientes" sheetId="2" r:id="rId2"/><sheet name="Velha" sheetId="1" r:id="rId1"/></sheets></workbook>')
        z.writestr('xl/_rels/workbook.xml.rels', '<Relationships><Relationship Id="rId1" Target="worksheets/sheet1.xml"/><Relationship Target="worksheets/sheet2.xml" Id="rId2"/></Relationships>')
        z.writestr('xl/worksheets/sheet1.xml', folha(111))
        z.writestr('xl/worksheets/sheet2.xml', folha(222))
    assert assessor.ler_planilha(p)[0]['conta_xp'] == '222'


def test_telefone_normalizado_ou_bloqueado():
    for bruto in ('11 98765-4321', '+55 (11) 98765-4321', '011 98765-4321', '5511987654321'):
        assert assessor.tel_br(bruto) == ('+5511987654321', None), bruto
    for bruto in ('', '98765-4321', '20 98765-4321', '11 88765-4321'):
        tel, erro = assessor.tel_br(bruto)
        assert tel is None and erro, bruto


def test_discurso_preserva_blocos_e_le_referencia():
    p = BASE / 'discurso.md'
    p.write_text('<!-- referência: 10/2026 -->\n# titulo\n*Brasil:* a\n\n\n\n*Mundo:* b  \n', encoding='utf-8')
    assert assessor.ler_discurso(p) == ('*Brasil:* a\n\n*Mundo:* b', (10, '2026'))


def test_ancoras_usam_quebra_real():
    longa = 'palavra ' * 40
    assert assessor.ancoras('Olá, Ana!\n\n' + longa + '\n \n\nAbraço!\n') == ('Olá, Ana!', 'Abraço!', 3)
    ref = '2026-09-30'
    out = BASE / f'lote-{ref}'
    (out / '9').mkdir(parents=True)
    (out / '9' / 'mensagem.txt').write_text('Olá, Ana!\n\nUma linha só, mesmo longa\n\nAbraço!\n', encoding='utf-8')
    with open(out / 'conferir-envios.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(assessor.CAB_LOTE)
        w.writerow(['9', 'Ana', 'Ana', '+5511987654321', 'pronto', '', ''])
    saida, cod = rodar(assessor.texto, ref, '9')
    assert cod == 0 and saida.splitlines() == ['LINHAS 3', 'PRIMEIRA Olá, Ana!', 'ULTIMA Abraço!']
    saida, cod = rodar(assessor.texto, ref, '8')
    assert cod and 'nao esta no lote' in str(cod)
    (out / '9' / 'mensagem.txt').write_text('\n  \n', encoding='utf-8')
    saida, cod = rodar(assessor.texto, ref, '9')
    assert cod and 'sem linha' in str(cod)


def test_estado_do_lote():
    ref = '2026-10-31'
    out = BASE / f'lote-{ref}'
    for c in ('1', '2', '3'):
        (out / c).mkdir(parents=True)
        (out / c / 'relatorio.pdf').write_bytes(b'%PDF ' + c.encode())
        (out / c / 'mensagem.txt').write_text('msg ' + c, encoding='utf-8')
    with open(out / 'conferir-envios.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(assessor.CAB_LOTE)
        w.writerow(['1', 'Ana', 'Ana', '+5511987654321', 'pronto', '', ''])
        w.writerow(['2', 'Bia', 'Bia', '+5511987654322', 'revisar', 'conta repetida no zip', ''])
        w.writerow(['3', 'Caio', 'Caio', '', 'bloqueado', 'sem telefone', ''])
    cod = assessor.codigo(out)

    # sem aprovação não há fila
    assert rodar(assessor.checar, ref)[1] == 1
    # aprovação presa ao conteúdo mostrado
    assert rodar(assessor.aprovar, ref, 'deadbeef')[1]
    assert rodar(assessor.aprovar, ref, cod, '1')[1]  # conta 1 não é revisar
    assert rodar(assessor.aprovar, ref, cod)[1] == 0

    # log de versão anterior (envios.csv) é migrado e continua valendo
    (BASE / 'envios.csv').write_text(','.join(assessor.CAB_ENVIOS) + f'\n2026-11-01,{ref},3,Caio,pulado: sem telefone,09:00\n', encoding='utf-8')
    saida, st = rodar(assessor.checar, ref)
    assert st == 0 and 'ENVIAR 1 |' in saida and 'PULAR 2 | revisar nao aprovado' in saida and 'JA_REGISTRADO 3 | pulado: sem telefone' in saida
    assert (BASE / 'historico-envios.csv').is_file() and not (BASE / 'envios.csv').exists()

    # motivo com vírgula não quebra o log; conta registrada sai da fila
    assert rodar(assessor.registrar, ref, '1', 'falhou: contato ambíguo, nomes: Ana A, Ana B')[1] == 0
    assert rodar(assessor.registrar, ref, '1', 'mandei')[1]
    assert rodar(assessor.registrar, ref, '9', 'enviado')[1]
    saida, st = rodar(assessor.checar, ref)
    assert st == 0 and 'JA_REGISTRADO 1 | falhou: contato ambíguo, nomes: Ana A, Ana B' in saida

    # lote alterado depois da aprovação bloqueia
    (out / '1' / 'mensagem.txt').write_text('msg alterada', encoding='utf-8')
    saida, st = rodar(assessor.checar, ref)
    assert st == 1 and 'mudou depois da aprovacao' in saida
    (out / '1' / 'mensagem.txt').write_text('msg 1', encoding='utf-8')

    # linha corrompida no log bloqueia
    with open(BASE / 'historico-envios.csv', 'a', encoding='utf-8') as fh:
        fh.write('2026-11-09,2026-10-31,2,Bia,enviado\n')
    saida, st = rodar(assessor.checar)
    assert st == 1 and 'linha 4: 5 colunas' in saida


def test_conferir_caixa_paragrafos():
    p = BASE / 'caixa.txt'
    linhas = [f'paragrafo {i}' for i in range(1, 11)]
    p.write_text('\n\n'.join(linhas) + '\n', encoding='utf-8')
    os.environ['ASSESSOR_CLIPBOARD'] = '\n'.join(linhas)
    try:
        saida, cod = rodar(assessor.conferir_caixa, str(p))
        assert cod == 0 and saida.strip() == 'bate', saida
        outro = linhas.copy()
        outro[6] = 'outro'
        os.environ['ASSESSOR_CLIPBOARD'] = '\n'.join(outro)
        saida, cod = rodar(assessor.conferir_caixa, str(p))
        assert cod != 0 and saida.strip() == 'nao bate: parágrafo 7 diferente', saida
        os.environ['ASSESSOR_CLIPBOARD'] = '\n'.join(linhas[:7])
        saida, cod = rodar(assessor.conferir_caixa, str(p))
        assert cod != 0 and saida.strip() == 'nao bate: 3 faltando', saida
        curto = linhas[:7]
        curto[6] = 'outro'
        os.environ['ASSESSOR_CLIPBOARD'] = '\n'.join(curto)
        saida, cod = rodar(assessor.conferir_caixa, str(p))
        assert cod != 0 and saida.strip() == 'nao bate: parágrafo 7 diferente, 3 faltando', saida
        os.environ['ASSESSOR_CLIPBOARD'] = '\n'.join(linhas + ['extra'])
        saida, cod = rodar(assessor.conferir_caixa, str(p))
        assert cod != 0 and saida.strip() == 'nao bate: 1 sobrando', saida
        os.environ['ASSESSOR_CLIPBOARD'] = 'valor  cheio'
        p.write_text('valor cheio\n', encoding='utf-8')
        saida, cod = rodar(assessor.conferir_caixa, str(p))
        assert cod != 0 and saida.strip() == 'nao bate: parágrafo 1 diferente', saida
    finally:
        os.environ.pop('ASSESSOR_CLIPBOARD', None)


def test_conferir_caixa_crlf_nbsp():
    p = BASE / 'crlf.txt'
    p.write_text('valor\u00a0cheio\r\n\r\n  segunda  \r\n', encoding='utf-8')
    os.environ['ASSESSOR_CLIPBOARD'] = 'valor cheio\nsegunda'
    try:
        saida, cod = rodar(assessor.conferir_caixa, str(p))
        assert cod == 0 and saida.strip() == 'bate', saida
        p.write_text('valor cheio\nsegunda\n', encoding='utf-8')
        os.environ['ASSESSOR_CLIPBOARD'] = 'valor\u00a0cheio\r\n\r\nsegunda'
        saida, cod = rodar(assessor.conferir_caixa, str(p))
        assert cod == 0 and saida.strip() == 'bate', saida
    finally:
        os.environ.pop('ASSESSOR_CLIPBOARD', None)


def test_conferir_caixa_funcao_substituivel():
    p = BASE / 'fn.txt'
    p.write_text('aa\nbb\n', encoding='utf-8')
    os.environ.pop('ASSESSOR_CLIPBOARD', None)
    orig = assessor.ler_clipboard
    assessor.ler_clipboard = lambda: 'aa\nbb'
    try:
        saida, cod = rodar(assessor.conferir_caixa, str(p))
        assert cod == 0 and saida.strip() == 'bate', saida
    finally:
        assessor.ler_clipboard = orig


def test_copiar_caminho_ref_e_falhas():
    saida, cod = rodar(assessor.copiar, str(BASE / 'nao-existe.txt'))
    assert cod != 0 and saida.strip() == 'falhou: arquivo não encontrado', saida
    saida, cod = rodar(assessor.conferir_caixa, str(BASE / 'nao-existe.txt'))
    assert cod != 0 and saida.strip() == 'falhou: arquivo não encontrado', saida
    vazio = BASE / 'vazio.txt'
    vazio.write_text(' \n\n\t\n', encoding='utf-8')
    def clipboard_proibido():
        raise AssertionError('clipboard')
    orig_ler = assessor.ler_clipboard
    assessor.ler_clipboard = clipboard_proibido
    try:
        saida, cod = rodar(assessor.copiar, str(vazio))
        assert cod != 0 and saida.strip() == 'vazio', saida
        saida, cod = rodar(assessor.conferir_caixa, str(vazio))
        assert cod != 0 and saida.strip() == 'vazio', saida
    finally:
        assessor.ler_clipboard = orig_ler
    exato = 'um\n\n  dois  \n'
    cheio = BASE / 'cheio.txt'
    cheio.write_text(exato, encoding='utf-8')
    gravado = []
    orig = assessor.gravar_clipboard
    assessor.gravar_clipboard = gravado.append
    try:
        saida, cod = rodar(assessor.copiar, str(cheio))
        assert cod == 0 and saida.strip() == 'copiado' and gravado == [exato], saida
        ref = '2026-08-15'
        out = BASE / f'lote-{ref}'
        (out / '4').mkdir(parents=True)
        (out / '4' / 'mensagem.txt').write_text(exato, encoding='utf-8')
        with open(out / 'conferir-envios.csv', 'w', newline='', encoding='utf-8') as fh:
            w = csv.writer(fh)
            w.writerow(assessor.CAB_LOTE)
            w.writerow(['4', 'Cliente', 'Cliente', '', 'pronto', '', ''])
        gravado.clear()
        saida, cod = rodar(assessor.copiar, ref, '4')
        assert cod == 0 and saida.strip() == 'copiado' and gravado == [exato], saida
        os.environ['ASSESSOR_CLIPBOARD'] = 'um\ndois'
        saida, cod = rodar(assessor.conferir_caixa, ref, '4')
        assert cod == 0 and saida.strip() == 'bate', saida
        (out / '4' / 'mensagem.txt').unlink()
        saida, cod = rodar(assessor.copiar, ref, '4')
        assert cod != 0 and saida.strip() == 'falhou: arquivo não encontrado', saida
        saida, cod = rodar(assessor.copiar, ref, '5')
        assert cod != 0 and 'nao esta no lote' in saida, saida
    finally:
        assessor.gravar_clipboard = orig
        os.environ.pop('ASSESSOR_CLIPBOARD', None)


def test_copiar_sem_display_nao_chama_xclip():
    p = BASE / 'display.txt'
    p.write_text('oi\n', encoding='utf-8')
    orig = assessor.subprocess.run
    def vigia(*a, **k):
        raise AssertionError('xclip nao deveria rodar')
    assessor.subprocess.run = vigia
    antigo = os.environ.pop('DISPLAY', None)
    try:
        saida, cod = rodar(assessor.copiar, str(p))
        assert cod != 0 and saida.strip() == 'falhou: DISPLAY ausente; precisa ser o display do desktop do bot', saida
    finally:
        assessor.subprocess.run = orig
        if antigo is not None:
            os.environ['DISPLAY'] = antigo


def test_xclip_ausente_mensagem_clara():
    chamadas = []
    orig_which, orig_run = assessor.shutil.which, assessor.subprocess.run
    def which(nome, *a, **k):
        if nome == 'xclip':
            return None
        return orig_which(nome, *a, **k)
    def run(args, **k):
        chamadas.append((args, k))
        class R:
            returncode = 1
        return R()
    assessor.shutil.which = which
    assessor.subprocess.run = run
    try:
        saida, cod = rodar(assessor.garantir_xclip)
        assert cod != 0 and saida.strip() == 'falhou: xclip ausente e a instalacao silenciosa falhou', saida
        args, k = chamadas[0]
        assert args == ['sudo', '-n', 'env', 'DEBIAN_FRONTEND=noninteractive', 'apt-get', 'install', '-y', 'xclip']
        assert k.get('stdin') is assessor.subprocess.DEVNULL
        assert k.get('stdout') is assessor.subprocess.DEVNULL and k.get('stderr') is assessor.subprocess.DEVNULL
    finally:
        assessor.shutil.which = orig_which
        assessor.subprocess.run = orig_run


if __name__ == '__main__':
    for nome, f in list(globals().items()):
        if nome.startswith('test_'):
            f()
            print('ok', nome)

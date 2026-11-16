"""O dry run: transcript legível e métricas a partir do stream do ator, e a pasta do bot a partir da pasta do fluxo."""
import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]


def _dry_run():
    spec = importlib.util.spec_from_file_location('dry_run', RAIZ / 'scripts/dry-run.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _assistente(blocos, pai=None):
    return {'type': 'assistant', 'parent_tool_use_id': pai, 'message': {'content': blocos}}


def _usuario(blocos, pai=None):
    return {'type': 'user', 'parent_tool_use_id': pai, 'message': {'content': blocos}}


def test_legivel_numera_passos_liga_subagente_e_corta():
    dry = _dry_run()
    longo = 'x' * (dry.LIMITE + 500)
    eventos = [
        {'type': 'system', 'subtype': 'init', 'model': 'm', 'tools': ['Bash'], 'skills': ['analista-tese', 'dataviz'], 'agents': ['knowledgeWork']},
        {'type': 'rate_limit_event'},
        _assistente([{'type': 'tool_use', 'id': 'b1', 'name': 'Bash', 'input': {'command': 'python mercado.py tesouro'}}]),
        _usuario([{'type': 'tool_result', 'tool_use_id': 'b1', 'content': longo}]),
        _assistente([{'type': 'text', 'text': 'Rascunho pronto.'},
                     {'type': 'tool_use', 'id': 'a1', 'name': 'Agent', 'input': {'subagent_type': 'knowledgeWork', 'prompt': 'revise'}}]),
        # Prompt de subagente em texto puro, sem lista de blocos.
        _usuario('revise', pai='a1'),
        _assistente([{'type': 'text', 'text': 'Veredito: frágil'}], pai='a1'),
        _usuario([{'type': 'tool_result', 'tool_use_id': 'a1', 'content': [{'type': 'text', 'text': 'Veredito: frágil'}]}]),
        # Skill do Claude Code pode carregar sem estar no init: a marca vem do nome pedido.
        # A chamada que volta com erro é tentativa, não carga.
        _assistente([{'type': 'tool_use', 'id': 's1', 'name': 'Skill', 'input': {'skill': 'analista-tese'}},
                     {'type': 'tool_use', 'id': 's2', 'name': 'Skill', 'input': {'skill': 'artifact-design'}},
                     {'type': 'tool_use', 'id': 's3', 'name': 'Skill', 'input': {'skill': 'dataviz'}}]),
        _usuario([{'type': 'tool_result', 'tool_use_id': 's2', 'content': 'Launching skill: artifact-design'},
                  {'type': 'tool_result', 'tool_use_id': 's3', 'is_error': True, 'content': 'Unknown skill: dataviz'}]),
        {'type': 'result', 'subtype': 'success', 'num_turns': 3, 'duration_ms': 10, 'result': 'Page: page.md',
         'permission_denials': [{'tool_name': 'PowerShell'}]},
    ]
    linhas = [json.dumps(e) for e in eventos]
    # Aviso em texto no stdout e última linha cortada não derrubam a conversão.
    linhas[1:1] = ['aviso solto no stdout']
    texto = dry.legivel(linhas + ['', '{"type": "assist'], ['analista-tese'])

    assert 'skills: analista-tese, dataviz' in texto
    # Skill de fora do bot, vista no init ou chamada, fica marcada logo abaixo do título.
    assert texto.startswith('# Transcript do ator\n\n## fora do bot\n\nno init: dataviz\n\n'
                            'chamadas: artifact-design (passo 4, ator); dataviz (passo 5, ator, recusada)\n\n')
    assert '## passo 3: ator chama Skill (analista-tese)\n' in texto
    assert '## passo 4: ator chama Skill (artifact-design) [fora do bot]\n' in texto
    assert 'fora do bot' not in dry.legivel([json.dumps(eventos[0])], ['analista-tese', 'dataviz'])
    assert '## passo 1: ator chama Bash (Bash)\n\n```\npython mercado.py tesouro\n```' in texto
    # O resultado longo é cortado e aponta a linha do jsonl (5ª linha do stream).
    assert '### resultado do passo 1 (Bash), para ator' in texto
    assert f'[cortado: {dry.LIMITE} de {dry.LIMITE + 500} caracteres; integra no transcript.jsonl, linha 5]' in texto
    assert longo not in texto
    assert '## passo 2: ator chama Agent (knowledgeWork)' in texto
    # O que o subagente recebe e responde aponta o passo que o chamou.
    assert '### entrada para subagente knowledgeWork do passo 2\n\nrevise' in texto
    assert '### texto de subagente knowledgeWork do passo 2\n\nVeredito: frágil' in texto
    assert '### resultado do passo 2 (knowledgeWork), para ator\n\n```\nVeredito: frágil\n```' in texto
    assert 'turnos: 3' in texto and 'PowerShell' in texto and texto.index('Rascunho pronto.') < texto.index('passo 2')
    assert '## linha 2 fora do JSON\n\n```\naviso solto no stdout\n```' in texto
    assert '## linha 14 fora do JSON\n\n```\n{"type": "assist\n```' in texto


def test_pasta_do_bot_e_fluxo_invalido(tmp_path):
    dry = _dry_run()
    assert dry.pasta_do_bot(RAIZ / 'evals/assessor/envio/fluxo/preparo') == RAIZ / 'bots/assessor/envio'
    # Fora de evals/<bot>/fluxo/<fluxo>, ou com seção faltando no cenário, para com mensagem e não com traceback.
    with pytest.raises(SystemExit, match='nao esta em evals'):
        dry.pasta_do_bot(tmp_path)
    (tmp_path / 'cenario.md').write_text('## Pedido\n\noi\n', encoding='utf-8')
    with pytest.raises(SystemExit, match="sem a secao '## Plataforma'"):
        dry.secao(tmp_path / 'cenario.md', 'Plataforma')


def test_copia_da_rodada_para_a_pasta_de_dados(tmp_path):
    dry = _dry_run()
    env = tmp_path / '.env'
    assert dry.pasta_de_dados(env) is None
    dados = tmp_path / 'dados com espaço'
    dados.mkdir()
    env.write_text(f'OUTRA=1\n{dry.VAR_DADOS}="{dados}"\n', encoding='utf-8')
    assert dry.pasta_de_dados(env) == dados.resolve()
    # Caminho relativo vale a partir da pasta do .env.
    env.write_text(f'{dry.VAR_DADOS}=dados com espaço\n', encoding='utf-8')
    assert dry.pasta_de_dados(env) == dados.resolve()

    execucao = tmp_path / 'execucao'
    (execucao / 'tmp').mkdir(parents=True)
    (execucao / 'tmp' / 'rascunho.md').write_text('tese', encoding='utf-8')
    bot, fluxo = RAIZ / 'bots/assessor/envio', RAIZ / 'evals/assessor/envio/fluxo/preparo'
    primeira = dry.arquivar(execucao, bot, fluxo, dados)
    segunda = dry.arquivar(execucao, bot, fluxo, dados)

    # A pasta do bot de dois níveis é mantida, e a segunda rodada do dia não sobrescreve a primeira.
    assert primeira.parent == dados / 'execucoes' / 'assessor' / 'envio'
    assert primeira.name == f'{dry.date.today().isoformat()}-preparo-dry-run'
    assert segunda.name == primeira.name + '-2'
    assert (primeira / 'tmp' / 'rascunho.md').read_text(encoding='utf-8') == 'tese'


def _escrever(caminho, texto):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding='utf-8')


def test_gosto_sobrepoe_variante_copia_partida_e_indexa(tmp_path, monkeypatch):
    dry = _dry_run()
    monkeypatch.setattr(dry, 'ROOT', tmp_path)
    bot, pergunta = tmp_path / 'bots/bot', tmp_path / 'evals/bot/gosto/pergunta'
    _escrever(bot / 'bot.md', '## Perfil\n\nperfil do bot\n')
    _escrever(bot / 'skills/um/SKILL.md', 'um original')
    _escrever(bot / 'skills/dois/SKILL.md', 'dois original')
    _escrever(pergunta / 'cenario.md', '## Pedido\n\npedido\n\n## Plataforma\n\nplataforma em {execucao}\n')
    _escrever(pergunta / 'variantes/base/.gitkeep', '')
    _escrever(pergunta / 'variantes/nova/skills/um/SKILL.md', 'um da variante')
    _escrever(pergunta / 'variantes/persona/bot.md', '## Perfil\n\nperfil da variante\n')
    variantes = dry.ler_variantes(pergunta, bot, [])
    assert [v[0] for v in variantes] == ['base', 'nova', 'persona']
    # O ## Perfil do bot.md da variante vai para o prompt de sistema no lugar do perfil do bot.
    assert variantes[2][3].startswith('perfil da variante') and variantes[0][3].startswith('perfil do bot')

    # Recusas antes de qualquer amostra: variante repetida, arquivo que o bot não tem
    # (inclusive só com maiúsculas diferentes) e partida com algo além de tmp/ e workspace/.
    with pytest.raises(SystemExit, match='repetida'):
        dry.ler_variantes(pergunta, bot, ['nova', 'nova'])
    for errado in ('skills/um/SKILL.md.bak', 'skills/um/skill.md', 'skills/tres/SKILL.md'):
        _escrever(tmp_path / 'errada' / errado, 'x')
        with pytest.raises(SystemExit, match='so sobrepoe'):
            dry.arquivos_da_variante(tmp_path / 'errada', bot)
        (tmp_path / 'errada' / errado).unlink()
    partida = tmp_path / 'partida'
    _escrever(partida / '.claude/skills/um/SKILL.md', 'um de outra rodada')
    with pytest.raises(SystemExit, match=r'tire: \.claude'):
        dry.ler_partida(partida)
    shutil.rmtree(partida / '.claude')
    _escrever(partida / 'tmp/rascunho.md', 'rascunho congelado')
    assert dry.ler_partida(partida) == partida

    vistos = []

    def ator_falso(claude, fluxo, pedido, sistema, dest, modelo):
        assert modelo == 'haiku'
        vistos.append(dest.name)
        assert pedido == 'pedido' and sistema.endswith(f'plataforma em {dest.as_posix()}')
        if dest.name != 'persona-2':
            (dest / 'page.html').write_text('<p>page</p>', encoding='utf-8')
            (dest / 'transcript.md').write_text('t', encoding='utf-8')
        if dest.name == 'nova-1':
            carga = _assistente([{'type': 'tool_use', 'id': 's1', 'name': 'Skill', 'input': {'skill': 'dataviz'}}])
            (dest / 'transcript.md').write_text(dry.legivel([json.dumps(carga)], ['um', 'dois']), encoding='utf-8')
        return 0

    monkeypatch.setattr(dry, 'atuar', ator_falso)
    rodada = tmp_path / 'rodada'
    rodada.mkdir()
    dry.gosto('claude', pergunta, bot, variantes, 2, partida, rodada, 'haiku')

    # Uma amostra de cada variante por volta.
    assert vistos == ['base-1', 'nova-1', 'persona-1', 'base-2', 'nova-2', 'persona-2']
    for nome in vistos:
        skills = rodada / nome / '.claude/skills'
        um = 'um da variante' if nome.startswith('nova') else 'um original'
        assert (skills / 'um/SKILL.md').read_text(encoding='utf-8') == um
        assert (skills / 'dois/SKILL.md').read_text(encoding='utf-8') == 'dois original'
        assert (rodada / nome / 'tmp/rascunho.md').read_text(encoding='utf-8') == 'rascunho congelado'
        assert (rodada / nome / 'workspace').is_dir()
    indice = (rodada / 'index.html').read_text(encoding='utf-8')
    assert '<a href="nova-1/page.html">nova-1</a>' in indice and '<a href="nova-1/transcript.md">' in indice
    # Amostra que caiu sem transcript aponta o ator.err.
    assert 'persona-2: sem page.html' in indice and '<a href="persona-2/ator.err">' in indice
    assert indice.index('<th>base</th>') < indice.index('base-2/page.html') < indice.index('<th>nova</th>')
    # A carga de skill de fora do bot aparece na célula da amostra, e só nela.
    marca = '<strong>fora do bot: chamadas dataviz (passo 1, ator); no init nenhuma</strong>'
    assert indice.count('fora do bot') == 1 and indice.index('nova-1/transcript.md') < indice.index(marca) < indice.index('nova-2')


def _rodada(pasta, ator, mensagens, minutos, uso, fim='success'):
    """Stream fictício: `mensagens` é a lista de (pai, id, modelo) de cada evento assistant e `uso` dá (entrada, saída) por modelo."""
    eventos = [{'type': 'system', 'subtype': 'init', 'model': ator}]
    eventos += [_assistente([], pai=pai) | {'message': {'id': i, 'model': m, 'content': []}} for pai, i, m in mensagens]
    tokens = {m: {'inputTokens': e, 'outputTokens': s} | ({'cacheReadInputTokens': 1000, 'cacheCreationInputTokens': 200} if m == ator else {})
              for m, (e, s) in uso.items()}
    if fim:
        eventos.append({'type': 'result', 'subtype': fim, 'num_turns': len(mensagens) + 1,
                        'duration_ms': minutos * 60000, 'modelUsage': tokens})
    # Linha solta, JSON que não é objeto e assistant sem message não derrubam a leitura.
    _escrever(pasta / 'transcript.jsonl', '\n'.join(json.dumps(e) for e in eventos) + '\naviso solto\n3\n{"type": "assistant"}\n')


def test_tabela_de_metricas_por_modelo(tmp_path, capsys):
    dry = _dry_run()
    a, b, sub = 'modelo-a', 'modelo-b', 'modelo-sub'
    # Resposta com vários blocos chega em vários eventos com o mesmo id: conta uma requisição.
    # A mensagem do subagente (com pai) conta no modelo dela.
    _rodada(tmp_path / 'a/rodada-1', a, [(None, 'm1', a), (None, 'm1', a), (None, 'm2', a), ('t1', 's1', sub)], 2,
            {a: (10, 100), sub: (20, 30)})
    # O modelo que a ferramenta chama por dentro tem tokens e nenhuma mensagem no stream.
    _rodada(tmp_path / 'a/rodada-2', a, [(None, 'm1', a)], 4, {a: (10, 1300), 'claude-interno': (5, 1)})
    _rodada(tmp_path / 'a/rodada-3', a, [(None, 'm1', a), (None, 'm2', a)], 3, {a: (10, 700)})
    _rodada(tmp_path / 'b', b, [(None, 'm1', b)], 1, {b: (10, 50)})
    # Ator que caiu antes do result, ou com result de erro, fica fora da tabela, com aviso.
    _rodada(tmp_path / 'a/rodada-4', a, [(None, 'm1', a)] * 9, 9, {a: (9, 9)}, fim=None)
    _rodada(tmp_path / 'a/rodada-5', a, [(None, 'm1', a)] * 9, 9, {a: (9, 9)}, fim='error_max_turns')

    texto = dry.tabela([tmp_path / 'a', tmp_path / 'b'])

    assert texto.splitlines() == [
        '| ator | rodadas | turnos | minutos |',
        '| --- | --- | --- | --- |',
        '| modelo-a | 3 | 3 (2 a 5) | 3 (2 a 4) |',
        '| modelo-b | 1 | 2 | 1 |',
        '',
        '| ator | modelo | requisicoes no stream | entrada | cache lido | cache gravado | saida |',
        '| --- | --- | --- | --- | --- | --- | --- |',
        # Cada modelo com os seus tokens, nunca somados sob o nome do ator; rodada sem o modelo entra com zero.
        '| modelo-a | claude-interno | 0 | 0 (0 a 5) | 0 | 0 | 0 (0 a 1) |',
        '| modelo-a | modelo-a | 2 (1 a 2) | 10 | 1.000 | 200 | 700 (100 a 1.300) |',
        '| modelo-a | modelo-sub | 0 (0 a 1) | 0 (0 a 20) | 0 | 0 | 0 (0 a 30) |',
        '| modelo-b | modelo-b | 1 | 10 | 1.000 | 200 | 50 |',
    ]
    erro = capsys.readouterr().err
    assert 'rodada-4' in erro and 'rodada-5' in erro
    assert dry.tabela([tmp_path / 'vazia']) == ''


def test_rodadas_seguem_quando_ator_ou_avaliador_falham(tmp_path, monkeypatch, capsys):
    dry = _dry_run()
    monkeypatch.setattr(dry.shutil, 'which', lambda nome: 'claude')
    monkeypatch.setattr(dry, 'pasta_de_dados', lambda: None)
    avaliadas = []

    def ator_falso(claude, fluxo, pedido, sistema, dest, modelo):
        _rodada(dest, modelo, [(None, 'm1', modelo)], 1, {modelo: (10, 5)})
        (dest / 'transcript.md').write_text('t', encoding='utf-8')
        return 1 if dest.name == 'rodada-3' else 0

    def avaliador_falso(claude, fluxo, dest, cenario=None):
        avaliadas.append(dest.name)
        if dest.name == 'rodada-1':
            raise RuntimeError('o avaliador falhou (exit 1): x')
        return 'relatorio'

    monkeypatch.setattr(dry, 'atuar', ator_falso)
    monkeypatch.setattr(dry, 'avaliar', avaliador_falso)
    saida = tmp_path / 'execucao'
    monkeypatch.setattr(sys, 'argv', ['dry-run.py', str(RAIZ / 'evals/analista/fluxo/tese'), '--rodadas', '3',
                                      '--modelo', 'haiku', '--saida', str(saida)])
    with pytest.raises(SystemExit) as fim:
        dry.main()

    # A falha do avaliador na 1ª rodada não impede a 2ª e a 3ª; a 3ª, com o ator em erro, não é avaliada.
    assert avaliadas == ['rodada-1', 'rodada-2']
    assert [(p.name, (p / 'relatorio.md').is_file()) for p in sorted(saida.iterdir())] == [
        ('rodada-1', False), ('rodada-2', True), ('rodada-3', False)]
    assert 'o avaliador falhou' in str(fim.value) and 'rodada-1' in str(fim.value) and 'exit 1' in str(fim.value)
    # A tabela sai mesmo com rodada incompleta, com as três rodadas do ator.
    assert '| haiku | 3 |' in capsys.readouterr().out

    # Pasta de --metricas com erro de digitação para o script, mesmo com outra pasta válida.
    monkeypatch.setattr(sys, 'argv', ['dry-run.py', '--metricas', str(saida), str(tmp_path / 'nao-existe')])
    with pytest.raises(SystemExit, match='nao existe'):
        dry.main()


def test_cenarios_do_fluxo_rodam_todos_com_a_plataforma_comum(tmp_path, monkeypatch, capsys):
    dry = _dry_run()
    repo = tmp_path / 'repo'
    monkeypatch.setattr(dry, 'ROOT', repo)
    monkeypatch.setattr(dry.shutil, 'which', lambda nome: 'claude')
    dados = tmp_path / 'dados'
    dados.mkdir()
    monkeypatch.setattr(dry, 'pasta_de_dados', lambda: dados)
    bot, fluxo = repo / 'bots/bot', repo / 'evals/bot/fluxo/tese'
    _escrever(bot / 'bot.md', '## Perfil\n\nperfil\n')
    _escrever(bot / 'skills/um/SKILL.md', 'um')
    _escrever(fluxo / 'plataforma.md', '## Plataforma\n\nplataforma comum\n')
    _escrever(fluxo / 'cenarios/acao.md', '## Pedido\n\npedido da acao\n')
    _escrever(fluxo / 'cenarios/titulo.md', '## Pedido\n\npedido do titulo\n')
    vistos, avaliados = {}, {}

    def ator_falso(claude, fluxo, pedido, sistema, dest, modelo):
        vistos[dest.name] = (pedido, sistema)
        (dest / 'page.md').write_text('# Tese\n\n| a | b |\n| - | - |\n| 1 | 2 |\n', encoding='utf-8')
        _rodada(dest, modelo, [(None, 'm1', modelo)], 1, {modelo: (10, 5)})
        (dest / 'transcript.md').write_text('t', encoding='utf-8')
        return 0

    def avaliador_falso(claude, fluxo, dest, cenario=None):
        avaliados[dest.name] = cenario.name
        return 'relatorio'

    monkeypatch.setattr(dry, 'atuar', ator_falso)
    monkeypatch.setattr(dry, 'avaliar', avaliador_falso)
    saida = tmp_path / 'execucao'

    # Com mais de um cenário, sem --cenario nem --all, para e lista os nomes.
    monkeypatch.setattr(sys, 'argv', ['dry-run.py', str(fluxo), '--saida', str(saida)])
    with pytest.raises(SystemExit, match='acao, titulo'):
        dry.main()
    for opcoes, erro in [(['--cenario', 'nada'], "'nada' nao existe"), (['--cenario', 'acao', '--all'], 'nao os dois'),
                         (['--cenario', 'acao', '--variantes'], 'so valem no modo de fluxo')]:
        monkeypatch.setattr(sys, 'argv', ['dry-run.py', str(fluxo), *opcoes, '--saida', str(saida)])
        with pytest.raises(SystemExit, match=erro):
            dry.main()
    # Fluxo com cenarios/ e cenario.md juntos para, em vez de ignorar um deles.
    _escrever(fluxo / 'cenario.md', '## Pedido\n\nsobra\n')
    monkeypatch.setattr(sys, 'argv', ['dry-run.py', str(fluxo), '--all', '--saida', str(saida)])
    with pytest.raises(SystemExit, match='cenarios/ e cenario.md'):
        dry.main()
    (fluxo / 'cenario.md').unlink()

    monkeypatch.setattr(sys, 'argv', ['dry-run.py', str(fluxo), '--all', '--saida', str(saida)])
    dry.main()
    # Cada cenário roda na sua pasta, com o próprio pedido e a plataforma comum, e é avaliado contra o próprio arquivo.
    assert vistos == {'acao': ('pedido da acao', 'perfil\n\nplataforma comum'),
                      'titulo': ('pedido do titulo', 'perfil\n\nplataforma comum')}
    assert avaliados == {'acao': 'acao.md', 'titulo': 'titulo.md'}
    assert (saida / 'acao' / 'relatorio.md').is_file() and (saida / 'titulo' / 'relatorio.md').is_file()
    # A Page em markdown ganha uma cópia em HTML, com a tabela renderizada.
    assert '<td>1</td>' in (saida / 'acao' / 'page.html').read_text(encoding='utf-8')
    # A cópia de cada cenário leva o nome dele.
    hoje = dry.date.today().isoformat()
    assert sorted(p.name for p in (dados / 'execucoes' / 'bot').iterdir()) == [
        f'{hoje}-tese-acao-dry-run', f'{hoje}-tese-titulo-dry-run']
    assert '## acao' in capsys.readouterr().out

    # Um cenário só, por --cenario, também leva o nome na cópia.
    monkeypatch.setattr(sys, 'argv', ['dry-run.py', str(fluxo), '--cenario', 'acao', '--saida', str(tmp_path / 'outra')])
    dry.main()
    assert (dados / 'execucoes' / 'bot' / f'{hoje}-tese-acao-dry-run-2').is_dir()

    # Um cenário que levanta exceção não tira a tabela nem o relatório do outro, e o script sai citando o cenário.
    def ator_que_quebra(claude, fluxo, pedido, sistema, dest, modelo):
        if dest.name == 'titulo':
            raise OSError('disco cheio')
        return ator_falso(claude, fluxo, pedido, sistema, dest, modelo)

    monkeypatch.setattr(dry, 'atuar', ator_que_quebra)
    capsys.readouterr()
    monkeypatch.setattr(sys, 'argv', ['dry-run.py', str(fluxo), '--all', '--saida', str(tmp_path / 'terceira')])
    with pytest.raises(SystemExit, match='cenario titulo parou com erro: OSError'):
        dry.main()
    assert (tmp_path / 'terceira' / 'acao' / 'relatorio.md').is_file()
    assert '| sonnet | 1 |' in capsys.readouterr().out.split('## titulo')[0].split('## acao')[1]

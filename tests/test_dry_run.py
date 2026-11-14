"""O dry run: transcript legível a partir do stream do ator e a pasta do bot a partir da pasta do fluxo."""
import importlib.util
import json
import shutil
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
        {'type': 'system', 'subtype': 'init', 'model': 'm', 'tools': ['Bash'], 'skills': ['analista-tese'], 'agents': ['knowledgeWork']},
        {'type': 'rate_limit_event'},
        _assistente([{'type': 'tool_use', 'id': 'b1', 'name': 'Bash', 'input': {'command': 'python mercado.py tesouro'}}]),
        _usuario([{'type': 'tool_result', 'tool_use_id': 'b1', 'content': longo}]),
        _assistente([{'type': 'text', 'text': 'Rascunho pronto.'},
                     {'type': 'tool_use', 'id': 'a1', 'name': 'Agent', 'input': {'subagent_type': 'knowledgeWork', 'prompt': 'revise'}}]),
        # Prompt de subagente em texto puro, sem lista de blocos.
        _usuario('revise', pai='a1'),
        _assistente([{'type': 'text', 'text': 'Veredito: frágil'}], pai='a1'),
        _usuario([{'type': 'tool_result', 'tool_use_id': 'a1', 'content': [{'type': 'text', 'text': 'Veredito: frágil'}]}]),
        {'type': 'result', 'subtype': 'success', 'num_turns': 3, 'duration_ms': 10, 'result': 'Page: page.md',
         'permission_denials': [{'tool_name': 'PowerShell'}]},
    ]
    linhas = [json.dumps(e) for e in eventos]
    # Aviso em texto no stdout e última linha cortada não derrubam a conversão.
    linhas[1:1] = ['aviso solto no stdout']
    texto = dry.legivel(linhas + ['', '{"type": "assist'])

    assert 'skills: analista-tese' in texto
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
    assert '## linha 12 fora do JSON\n\n```\n{"type": "assist\n```' in texto


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

    def ator_falso(claude, fluxo, pedido, sistema, dest):
        vistos.append(dest.name)
        assert pedido == 'pedido' and sistema.endswith(f'plataforma em {dest.as_posix()}')
        if dest.name != 'persona-2':
            (dest / 'page.html').write_text('<p>page</p>', encoding='utf-8')
            (dest / 'transcript.md').write_text('t', encoding='utf-8')
        return 0

    monkeypatch.setattr(dry, 'atuar', ator_falso)
    rodada = tmp_path / 'rodada'
    rodada.mkdir()
    dry.gosto('claude', pergunta, bot, variantes, 2, partida, rodada)

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

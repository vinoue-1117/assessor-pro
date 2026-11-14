"""O dry run: transcript legível a partir do stream do ator e a pasta do bot a partir da pasta do fluxo."""
import importlib.util
import json
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

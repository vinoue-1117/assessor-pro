"""O transcript legível do dry run numera as chamadas, liga resultado e subagente ao passo e corta bloco longo."""
import importlib.util
import json
from pathlib import Path

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
        _usuario([{'type': 'text', 'text': 'revise'}], pai='a1'),
        _assistente([{'type': 'text', 'text': 'Veredito: frágil'}], pai='a1'),
        _usuario([{'type': 'tool_result', 'tool_use_id': 'a1', 'content': [{'type': 'text', 'text': 'Veredito: frágil'}]}]),
        {'type': 'result', 'subtype': 'success', 'num_turns': 3, 'duration_ms': 10, 'result': 'Page: page.md',
         'permission_denials': [{'tool_name': 'PowerShell'}]},
    ]
    texto = dry.legivel([json.dumps(e) for e in eventos] + [''])

    assert 'skills: analista-tese' in texto
    assert '## passo 1: ator chama Bash (Bash)\n\n```\npython mercado.py tesouro\n```' in texto
    # O resultado longo é cortado e aponta a linha do jsonl (4ª linha do stream).
    assert '### resultado do passo 1 (Bash), para ator' in texto
    assert f'[cortado: {dry.LIMITE} de {dry.LIMITE + 500} caracteres; integra no transcript.jsonl, linha 4]' in texto
    assert longo not in texto
    assert '## passo 2: ator chama Agent (knowledgeWork)' in texto
    # O que o subagente recebe e responde aponta o passo que o chamou.
    assert '### entrada para subagente knowledgeWork do passo 2\n\nrevise' in texto
    assert '### texto de subagente knowledgeWork do passo 2\n\nVeredito: frágil' in texto
    assert '### resultado do passo 2 (knowledgeWork), para ator\n\n```\nVeredito: frágil\n```' in texto
    assert 'turnos: 3' in texto and 'PowerShell' in texto and texto.index('Rascunho pronto.') < texto.index('passo 2')

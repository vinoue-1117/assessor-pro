"""A análise de live run: conversão do export do bot real para o transcript que o avaliador lê."""
import importlib.util
import json
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
SUB = 'sand-subagent-0000aaaa-1111-2222-3333-444455556666'


def _live_run():
    spec = importlib.util.spec_from_file_location('live_run', RAIZ / 'scripts/live-run.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _gravar(arquivo, eventos):
    arquivo.write_text('\n'.join(json.dumps(e, ensure_ascii=False) for e in eventos) + '\n', encoding='utf-8')


def _ev(papel, *blocos):
    return {'role': papel, 'message': {'content': list(blocos)}}


def _dono(marca, texto):
    return _ev('user', {'type': 'text', 'text': f'<user_query>\n[{marca}]\n[Sent from machine x]\n{texto}\n</user_query>'})


def _chamada(ident, nome, entrada):
    return _ev('assistant', {'type': 'tool_use', 'id': ident, 'name': nome, 'input': entrada})


def _resultado(ident, nome, texto):
    return _ev('tool', {'type': 'tool_result', 'tool_use_id': ident, 'name': nome, 'result': texto})


def _task(ident, tipo, resume=None):
    args = {'subagent_type': tipo, 'prompt': 'faca'} | ({'resume': SUB} if resume else {})
    return _chamada(ident, 'CallDynamicTool', {'namespace': 'n', 'toolName': 'Task', 'arguments': args})


def _export(pasta):
    _gravar(pasta / 'sessao.jsonl', [
        _ev('user', {'type': 'text', 'text': '<user_query>\n[GROK_BOT_HIDDEN_PROMPT][first run] instale\n</user_query>'}),
        _dono('t1u', 'instale o bot'),
        _chamada('c0', 'Shell', {'command': 'echo instalacao'}),
        _resultado('c0', 'Shell', 'ok'),
        _dono('t2u', 'escreva a tese'),
        _task('c1', 'executor'),
        _resultado('c1', 'CallDynamicTool', f'Subagent is running. Agent ID: {SUB}'),
        # O export repete chamada e resultado depois de um <memory_context>.
        _ev('user', {'type': 'text', 'text': '<memory_context>\nfatos\n</memory_context>'}),
        _task('c1', 'executor'),
        _resultado('c1', 'CallDynamicTool', f'Subagent is running. Agent ID: {SUB}'),
        _dono('t3u', 'pode publicar'),
        _task('c2', 'executor', resume=True),
        _resultado('c2', 'CallDynamicTool', f'Subagent is running. Agent ID: {SUB}'),
        _chamada('c3', 'SendToUser', {'content': 'Page publicada'}),
        _resultado('c3', 'SendToUser', 'Message sent to user'),
        _dono('t4u', 'exporte o transcript'),
        _chamada('c4', 'Shell', {'command': 'echo export'}),
        _resultado('c4', 'Shell', 'ok'),
    ])
    _gravar(pasta / f'subagente-{SUB}.jsonl', [
        _ev('user', {'type': 'text', 'text': 'prepare o rascunho'}),
        _chamada('s1', 'Shell', '{"command": "python mercado.py cotacao"}'),
        _resultado('s1', 'Shell', 'preco 10'),
        _ev('user', {'type': 'text', 'text': 'publique'}),
        _chamada('s2', 'WriteCanvas', json.dumps({'title': 'Tese', 'contents': '# Tese\n\nCompra.'})),
        _resultado('s2', 'WriteCanvas', 'ok'),
    ])


def test_converte_trecho_liga_subagente_retomado_e_descarta_repetidos(tmp_path):
    live = _live_run()
    _export(tmp_path)
    principal, subagentes = live.ler_export(tmp_path)
    assert [m for m, _, _ in live.mensagens_do_dono(live.ler(principal))] == ['t1u', 't2u', 't3u', 't4u']

    md, page = live.converter(principal, subagentes, 't2u', 't4u')

    # O trecho vai de [t2u] até antes de [t4u]: a instalação e o export ficam fora.
    assert 'echo instalacao' not in md and 'echo export' not in md
    assert '[t2u]' in md and '[t3u]' in md and '[t4u]' not in md.split('\n\n', 2)[2]
    passos = [linha for linha in md.splitlines() if linha.startswith('## passo ')]
    assert passos == [
        '## passo 1: bot chama CallDynamicTool (Task executor) [sessao.jsonl:6]',
        '## passo 2: subagente executor do passo 1 chama Shell (Shell) [subagente-' + SUB + '.jsonl:2]',
        '## passo 3: bot chama CallDynamicTool (Task executor, retomada) [sessao.jsonl:12]',
        '## passo 4: subagente executor do passo 3 chama WriteCanvas (WriteCanvas) [subagente-' + SUB + '.jsonl:5]',
        '## passo 5: bot chama SendToUser (SendToUser) [sessao.jsonl:14]',
    ]
    # Cada trecho do subagente entra depois do resultado da chamada que o iniciou ou retomou.
    assert md.index('resultado do passo 1') < md.index('prepare o rascunho') < md.index('passo 3: bot')
    assert md.index('resultado do passo 3') < md.index('### entrada para subagente executor do passo 3')
    assert 'resultado do passo ?' not in md and 'python mercado.py cotacao' in md
    assert page == '# Tese\n\nCompra.'


def test_formato_desconhecido_para_com_arquivo_e_linha(tmp_path):
    live = _live_run()
    _export(tmp_path)
    eventos = (tmp_path / 'sessao.jsonl').read_text(encoding='utf-8').splitlines()
    eventos.insert(2, json.dumps(_ev('assistant', {'type': 'image', 'source': 'x'})))
    (tmp_path / 'sessao.jsonl').write_text('\n'.join(eventos) + '\n', encoding='utf-8')
    with pytest.raises(live.FormatoDesconhecido, match=r'sessao\.jsonl:3'):
        live.ler(tmp_path / 'sessao.jsonl')

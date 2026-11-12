"""O gerador de ponteiros só aceita bot em que o bot.md e as skills batem."""
import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/gerar-ponteiros.py'
SKILL = "---\nname: {nome}\ndescription: 'completa'\n---\n"


def carregar_em(raiz):
    spec = importlib.util.spec_from_file_location('gerar_ponteiros', SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.ROOT, mod.BOTS = raiz, raiz / 'bots'
    return mod


def escrever(path, texto):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(texto, encoding='utf-8', newline='\n')


def test_bot_md_e_skills_precisam_bater(tmp_path):
    mod = carregar_em(tmp_path)
    bot = tmp_path / 'bots/exemplo'
    ficha = "# Exemplo\n\n## Perfil\n\nTexto.\n\n## Skills\n\n- `exemplo-core`: Use sempre.\n\n## Rotinas\n\n- não é skill\n"
    escrever(bot / 'bot.md', ficha)
    escrever(bot / 'skills/exemplo-core/SKILL.md', SKILL.format(nome='exemplo-core'))

    # caminho errado no bloco ## Instalar
    escrever(bot / 'README.md', (
        "## Instalar\n\n"
        "Atualize suas skills pelo Assessor Pro, caminho outro, "
        f"seguindo {mod.RAW}/bots/instalar.md.\n"
    ))
    with pytest.raises(SystemExit, match='prompt de instalacao'):
        mod.carregar()

    # URL do instalar.md fora do bloco ## Instalar
    escrever(bot / 'README.md', (
        f"seguindo {mod.RAW}/bots/instalar.md.\n\n"
        "## Instalar\n\n"
        "caminho exemplo,\n"
    ))
    with pytest.raises(SystemExit, match='prompt de instalacao'):
        mod.carregar()

    # caminho certo e a URL do instalar.md no mesmo bloco
    escrever(bot / 'README.md', (
        "## Instalar\n\n"
        "Atualize suas skills pelo Assessor Pro, caminho exemplo, "
        f"seguindo {mod.RAW}/bots/instalar.md.\n"
    ))

    esperado = mod.carregar()
    mod.gravar(esperado)
    mod.conferir(esperado)
    ponteiro = (bot / 'ponteiros/exemplo-core/SKILL.md').read_text(encoding='utf-8')
    assert "description: 'Use sempre.'" in ponteiro
    assert '/stable/bots/exemplo/skills/exemplo-core/SKILL.md' in ponteiro
    assert 'diga ao dono do bot: "Não consegui baixar as instruções atuais. Tente de novo em alguns minutos."' in ponteiro
    assert 'Assessor Pro' not in ponteiro
    assert 'diga ao assessor' not in ponteiro.lower()

    # ponteiro editado à mão ou de skill que saiu: a conferência acusa
    escrever(bot / 'ponteiros/exemplo-velha/SKILL.md', ponteiro)
    with pytest.raises(SystemExit):
        mod.conferir(esperado)

    # skill sem linha no bot.md
    escrever(bot / 'skills/exemplo-nova/SKILL.md', SKILL.format(nome='exemplo-nova'))
    with pytest.raises(SystemExit, match='exemplo-nova'):
        mod.carregar()

    # linha no bot.md sem skill
    escrever(bot / 'bot.md', ficha.replace('Use sempre.\n', 'Use sempre.\n- `exemplo-nova`: Use.\n- `exemplo-fantasma`: Use.\n'))
    with pytest.raises(SystemExit, match=r'nao existe: exemplo-fantasma'):
        mod.carregar()

    # skill em pasta sem bot.md
    escrever(tmp_path / 'bots/solto/skills/solta/SKILL.md', SKILL.format(nome='solta'))
    with pytest.raises(SystemExit, match='sem bot.md'):
        mod.carregar()

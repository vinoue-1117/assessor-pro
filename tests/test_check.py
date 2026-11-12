"""A recusa de arquivo de dado olha a extensão de cada caminho recebido."""
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/check.py'


def nomes(*caminhos):
    return subprocess.run(
        [sys.executable, str(SCRIPT), '--nomes'], input='\n'.join(caminhos) + '\n',
        capture_output=True, text=True, encoding='utf-8',
    )


def test_nomes_recusa_dado_e_aceita_o_resto():
    r = nomes('bots/exemplo/bot.md', 'bots/exemplo/Clientes.XLSM', 'assets/logo.png')
    assert r.returncode == 1 and '- bots/exemplo/Clientes.XLSM' in r.stderr and 'bot.md' not in r.stderr, r
    r = nomes('bots/exemplo/bot.md', 'assets/logo.png')
    assert r.returncode == 0 and r.stdout.strip() == 'dados ok', r

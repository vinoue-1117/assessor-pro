"""O instalar.md separa escopo bot (time) de user (bot pessoal).

O arquivo é o procedimento que o bot executa. Estas conferências travam as
frases que mudam o que ele apaga quando a biblioteca pessoal é compartilhada.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALAR = (ROOT / "bots" / "instalar.md").read_text(encoding="utf-8")
BOTS_README = (ROOT / "bots" / "README.md").read_text(encoding="utf-8")


def test_time_grava_no_escopo_bot_e_pessoal_cai_para_user():
    assert 'scope: "bot"' in INSTALAR
    assert "cannot keep skills of its own" in INSTALAR
    assert 'scope: "user"' in INSTALAR
    assert "Não grave estes ponteiros na biblioteca pessoal" in INSTALAR
    assert "não apague lá skill nenhuma" in INSTALAR
    assert "sem gravar em `user`" in INSTALAR
    assert "O escopo global não recebe estes ponteiros." in INSTALAR
    assert "Não deixe o ponteiro só na memória." in INSTALAR


def test_orfa_no_user_e_so_a_url_deste_caminho():
    assert "bots/<caminho>/skills/<nome>/SKILL.md" in INSTALAR
    assert "URL de script (`/scripts/`) não é ponteiro." in INSTALAR
    assert "Não reconheça skill pelo prefixo do nome." in INSTALAR
    # outro bot na mesma biblioteca, skill pessoal e citação de script ficam
    assert "sem listar e sem apagar" in INSTALAR
    assert "Não olhe a biblioteca pessoal." in INSTALAR
    assert "não grave por cima" in INSTALAR


def test_identidade_por_nome_nao_olha_a_biblioteca_pessoal():
    assert "A confirmação por nome de skill olha só o escopo `bot`." in INSTALAR
    assert "A biblioteca pessoal fica de fora dessa conta." in INSTALAR
    assert "não prova que este chat é o bot deste `bot.md`" in INSTALAR


def test_checklist_declara_o_escopo():
    assert "N de N ponteiros gravados no escopo <escopo>" in INSTALAR
    assert "troque `<escopo>` por `bot` ou `user`" in INSTALAR


def test_readme_dos_bots_nao_volta_a_dizer_que_so_o_bot_guarda_ponteiro():
    assert "biblioteca de skills do dono" in BOTS_README
    assert "bots/<caminho>/skills/<nome>/SKILL.md" in BOTS_README

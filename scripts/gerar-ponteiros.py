#!/usr/bin/env python3
"""Gera os ponteiros de cada bot a partir das skills completas.

Bot é toda pasta de bots/ que tem bot.md. As skills completas ficam em
<bot>/skills/ e os ponteiros gerados em <bot>/ponteiros/.

A description de cada ponteiro vem da seção "## Skills" do bot.md: uma
frase fixa sobre quando usar a skill. Ela não é copiada da skill completa,
então editar a description da skill completa não altera o ponteiro.

Uso:
  python scripts/gerar-ponteiros.py
  python scripts/gerar-ponteiros.py --check
"""
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOTS = ROOT / "bots"
RAW = "https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable"
FALHA = (
    "Não consegui baixar as instruções atuais do Assessor Pro. "
    "Tente de novo em alguns minutos."
)
ITEM = re.compile(r"^- `([a-z0-9-]+)`: (\S.*)$")


def rel(path):
    return path.relative_to(ROOT).as_posix()


def descricoes(ficha):
    """Lê as linhas "- `skill`: quando usar" da seção ## Skills do bot.md."""
    achadas, dentro = {}, False
    for linha in ficha.read_text(encoding="utf-8").split("\n"):
        if linha.startswith("## "):
            dentro = linha.strip() == "## Skills"
        elif dentro and linha.strip():
            m = ITEM.match(linha.rstrip())
            if not m:
                sys.exit(f"linha fora do formato em ## Skills de {rel(ficha)}: {linha}")
            if m[1] in achadas:
                sys.exit(f"skill repetida em ## Skills de {rel(ficha)}: {m[1]}")
            achadas[m[1]] = m[2]
    if not achadas:
        sys.exit(f"sem skill em ## Skills de {rel(ficha)}")
    return achadas


def frontmatter(text, path):
    if not text.startswith("---\n"):
        sys.exit(f"sem frontmatter: {path}")
    fim = text.find("\n---\n", 4)
    if fim == -1:
        sys.exit(f"frontmatter aberto: {path}")
    nome = descricao = None
    for linha in text[4:fim].split("\n"):
        if linha.startswith("name:"):
            nome = linha
        elif linha.startswith("description:"):
            descricao = linha
    if not nome or not descricao:
        sys.exit(f"frontmatter sem name ou description: {path}")
    if "\n" in nome or "\n" in descricao:
        sys.exit(f"name/description precisa ser uma linha: {path}")
    return nome, descricao


def carregar():
    """Devolve {caminho do ponteiro: texto} de todos os bots."""
    for path in sorted(BOTS.rglob("skills/*/SKILL.md")):
        if not (path.parents[2] / "bot.md").is_file():
            sys.exit(f"skill em pasta sem bot.md: {rel(path)}")
    esperado, nomes = {}, set()
    for ficha in sorted(BOTS.rglob("bot.md")):
        bot = ficha.parent
        descr = descricoes(ficha)
        achadas = set()
        for path in sorted(bot.glob("skills/*/SKILL.md")):
            nome_linha, _ = frontmatter(path.read_text(encoding="utf-8"), path)
            nome = nome_linha.split(":", 1)[1].strip().strip("'\"")
            if not nome:
                sys.exit(f"name vazio: {path}")
            if nome in nomes:
                sys.exit(f"nome de skill repetido: {nome}")
            if nome not in descr:
                sys.exit(f"skill sem linha em ## Skills de {rel(ficha)}: {nome}")
            nomes.add(nome)
            achadas.add(nome)
            dest = bot / "ponteiros" / nome / "SKILL.md"
            esperado[dest] = ponteiro(nome, nome_linha, rel(path), descr[nome])
        extras = sorted(set(descr) - achadas)
        if extras:
            sys.exit(f"{rel(ficha)} lista skill que não existe: " + ", ".join(extras))
    if not esperado:
        sys.exit(f"nenhum bot.md em {rel(BOTS)}")
    return esperado


def ponteiro(nome, nome_linha, caminho, descricao):
    url = f"{RAW}/{caminho}"
    destino = f"/workspace/assessor-pro/{nome}.md"
    desc_linha = "description: '" + descricao.replace("'", "''") + "'"
    return (
        "---\n"
        f"{nome_linha}\n"
        f"{desc_linha}\n"
        "---\n"
        "\n"
        "# Instruções atuais\n"
        "\n"
        "Baixe as instruções completas e siga somente o arquivo baixado.\n"
        "\n"
        f"1. `mkdir -p /workspace/assessor-pro && curl -fsSL {url} -o {destino}`\n"
        f"2. Confira que `{destino}` começa com frontmatter (`---`) e tem `{nome_linha}`.\n"
        "3. Siga exatamente o que foi baixado.\n"
        "\n"
        f'Se o download falhar, vier vazio ou a conferência não bater, pare e diga ao assessor: "{FALHA}" '
        "Não use cópia antiga nem improvise.\n"
    )


def refs_main():
    return [
        rel(path)
        for path in sorted(BOTS.rglob("SKILL.md"))
        if "/main/" in path.read_text(encoding="utf-8")
    ]


def gravar(esperado):
    for pasta in {dest.parents[1] for dest in esperado}:
        shutil.rmtree(pasta, ignore_errors=True)
    for dest, texto in esperado.items():
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(texto, encoding="utf-8", newline="\n")
    print(f"ponteiros gravados: {len(esperado)}")


def conferir(esperado):
    problemas = []
    for dest, texto in sorted(esperado.items()):
        if not dest.is_file():
            problemas.append(f"falta {rel(dest)}")
        elif dest.read_text(encoding="utf-8") != texto:
            problemas.append(f"desatualizado {rel(dest)}")
    for path in sorted(BOTS.rglob("ponteiros/*/SKILL.md")):
        if path not in esperado:
            problemas.append(f"ponteiro sobrando {rel(path)}")
    for item in refs_main():
        problemas.append(f"referencia /main/: {item}")
    if problemas:
        print("ponteiros desatualizados:", file=sys.stderr)
        for item in problemas:
            print(f"- {item}", file=sys.stderr)
        print("rode: python scripts/gerar-ponteiros.py", file=sys.stderr)
        sys.exit(1)
    print(f"ponteiros ok ({len(esperado)})")


def main():
    esperado = carregar()
    if "--check" not in sys.argv:
        gravar(esperado)
    conferir(esperado)


if __name__ == "__main__":
    main()

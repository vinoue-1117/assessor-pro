#!/usr/bin/env python3
"""Gera os ponteiros em template/skills a partir das skills completas.

Uso:
  python3 scripts/gerar-ponteiros.py
  python3 scripts/gerar-ponteiros.py --check
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ROOT / "plugins"
OUT = ROOT / "template" / "skills"
RAW = "https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable"
FALHA = (
    "Não consegui baixar as instruções atuais do Assessor Pro. "
    "Tente de novo em alguns minutos."
)


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


def skills():
    achadas = {}
    for path in sorted(PLUGINS.glob("*/skills/*/SKILL.md")):
        texto = path.read_text(encoding="utf-8")
        nome_linha, desc_linha = frontmatter(texto, path)
        nome = nome_linha.split(":", 1)[1].strip().strip("'\"")
        if not nome:
            sys.exit(f"name vazio: {path}")
        if nome in achadas:
            sys.exit(f"nome de skill repetido: {nome}")
        rel = path.relative_to(ROOT).as_posix()
        achadas[nome] = ponteiro(nome, nome_linha, desc_linha, rel)
    if not achadas:
        sys.exit(f"nenhuma skill em {PLUGINS}")
    return achadas


def ponteiro(nome, nome_linha, desc_linha, rel):
    url = f"{RAW}/{rel}"
    destino = f"/workspace/assessor-pro/{nome}.md"
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
    ruins = []
    for pasta in (PLUGINS, OUT):
        if not pasta.exists():
            continue
        for path in sorted(pasta.glob("*/skills/*/SKILL.md")) if pasta == PLUGINS else sorted(pasta.glob("*/SKILL.md")):
            if "/main/" in path.read_text(encoding="utf-8"):
                ruins.append(path.relative_to(ROOT).as_posix())
    return ruins


def gravar(esperado):
    OUT.mkdir(parents=True, exist_ok=True)
    for filho in list(OUT.iterdir()):
        if filho.is_dir() and filho.name not in esperado:
            for item in filho.rglob("*"):
                if item.is_file():
                    item.unlink()
            for item in sorted(filho.rglob("*"), reverse=True):
                if item.is_dir():
                    item.rmdir()
            filho.rmdir()
    for nome in sorted(esperado):
        dest = OUT / nome / "SKILL.md"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(esperado[nome], encoding="utf-8")
    print(f"ponteiros gravados: {len(esperado)}")


def conferir(esperado):
    problemas = []
    if not OUT.is_dir():
        problemas.append(f"falta o diretório {OUT.relative_to(ROOT)}")
    else:
        for nome, texto in sorted(esperado.items()):
            path = OUT / nome / "SKILL.md"
            if not path.is_file():
                problemas.append(f"falta {path.relative_to(ROOT)}")
            elif path.read_text(encoding="utf-8") != texto:
                problemas.append(f"desatualizado {path.relative_to(ROOT)}")
        for path in sorted(OUT.glob("*/SKILL.md")):
            if path.parent.name not in esperado:
                problemas.append(f"ponteiro sobrando {path.relative_to(ROOT)}")
    for rel in refs_main():
        problemas.append(f"referencia /main/: {rel}")
    if problemas:
        print("ponteiros desatualizados:", file=sys.stderr)
        for item in problemas:
            print(f"- {item}", file=sys.stderr)
        print("rode: python3 scripts/gerar-ponteiros.py", file=sys.stderr)
        sys.exit(1)
    print(f"ponteiros ok ({len(esperado)})")


def main():
    esperado = skills()
    if "--check" in sys.argv:
        conferir(esperado)
    else:
        gravar(esperado)
        conferir(esperado)


if __name__ == "__main__":
    main()

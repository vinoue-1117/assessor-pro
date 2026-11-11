#!/usr/bin/env python3
"""Valida o repositório: ponteiros, plugins gerados, template e testes.

Uso: python3 tools/check.py
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Montadas em partes para o próprio arquivo não carregar o texto que procura.
PALAVRA_PROIBIDA = "mol" + "de"
PREFIXOS_TOKEN = ("gh" + "p_", "github_" + "pat_", "gh" + "o_", "gl" + "pat-")
PULAR = {".git", "__pycache__", "node_modules"}


def run(args):
    print("+", " ".join(args))
    resultado = subprocess.run(args, cwd=ROOT)
    if resultado.returncode != 0:
        sys.exit(resultado.returncode)


def segredos():
    problemas = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(parte in PULAR for parte in path.parts):
            continue
        if path.suffix.lower() in {".png", ".pyc"}:
            continue
        bruto = path.read_bytes()
        if b"\0" in bruto:
            continue
        texto = bruto.decode("utf-8", "replace")
        baixo = texto.lower()
        rel = path.relative_to(ROOT).as_posix()
        if PALAVRA_PROIBIDA in baixo:
            problemas.append(f"palavra proibida ({PALAVRA_PROIBIDA}): {rel}")
        for prefixo in PREFIXOS_TOKEN:
            if prefixo in texto:
                problemas.append(f"prefixo de token {prefixo}: {rel}")
    if problemas:
        print("checagem de segredo falhou:", file=sys.stderr)
        for item in problemas:
            print(f"- {item}", file=sys.stderr)
        sys.exit(1)
    print("segredos ok")


def main():
    segredos()
    run(["python3", "tools/gerar-ponteiros.py", "--check"])
    run(["node", "tools/validate-template.mjs"])
    run(["python3", "bots/assessor/tests/test_assessor.py"])
    run(["python3", "-m", "pytest", "bots/assessor/tests/test_baixar_assessor.py"])


if __name__ == "__main__":
    main()

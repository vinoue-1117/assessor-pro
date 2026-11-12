#!/usr/bin/env python3
"""Porta de entrada do repositório: roda em toda PR e antes de cada commit.

Confere que nenhum arquivo de dado está versionado, que os ponteiros batem
com as skills e que os testes dos bots passam.

Uso: python scripts/check.py
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Formatos em que dado de cliente chega (lote, planilha, relatório).
# O repositório é público: nenhum deles entra, nem como amostra de teste.
DADOS = {".csv", ".pdf", ".xls", ".xlsx", ".zip"}


def versionados() -> list[str]:
    saida = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True
    ).stdout
    return [p for p in saida.decode("utf-8").split("\0") if p]


def rodar(*args: str) -> None:
    print("+", " ".join(args), flush=True)
    if subprocess.run([sys.executable, *args], cwd=ROOT).returncode != 0:
        sys.exit(1)


def main() -> None:
    dados = [p for p in versionados() if Path(p).suffix.lower() in DADOS]
    if dados:
        print("arquivo de dado versionado, tire do repo:", file=sys.stderr)
        for p in dados:
            print(f"- {p}", file=sys.stderr)
        sys.exit(1)
    rodar("scripts/gerar-ponteiros.py", "--check")
    rodar("-m", "pytest", "bots", "tests", "-q")
    print("check ok")


if __name__ == "__main__":
    main()

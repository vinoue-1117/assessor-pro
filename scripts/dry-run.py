#!/usr/bin/env python3
"""Dry run de um fluxo de bot: um ator faz o papel do bot e um avaliador lê o transcript.

O ator é um `claude -p` headless numa pasta de execução fora do repositório,
com as skills da branch em `.claude/skills/`, o `## Perfil` do `bot.md` e a
seção `## Plataforma` do cenário no prompt de sistema, e a seção `## Pedido`
como mensagem do dono. As instruções globais de quem roda (o CLAUDE.md e as
rules do usuário) ficam fora do contexto do ator.

Depois o agente `avaliador-transcript` lê o transcript contra as skills e o
`erros.md` do fluxo e escreve o relatório de desvios. Tudo fica na pasta de
execução: transcript.jsonl (o stream do ator), transcript.md (a versão
legível), page.md (se o ator publicou) e relatorio.md.

Roda pelo login do plano do Claude Code, sem chave de API.

Uso:
  python scripts/dry-run.py evals/analista/fluxo/tese [--saida PASTA]
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATOR = "sonnet"
AVALIADOR = "opus"
FERRAMENTAS = ["Bash", "Read", "Write", "Edit", "Glob", "Grep", "WebSearch", "WebFetch", "Agent", "Skill"]
# Caracteres de cada bloco no transcript legível. A íntegra fica no transcript.jsonl.
LIMITE = 4000


def secoes(texto):
    """Título de cada seção `## ` e o texto dela, sem o título."""
    partes = re.split(r"^## (.+)$", texto, flags=re.M)
    return {titulo.strip(): corpo.strip() for titulo, corpo in zip(partes[1::2], partes[2::2])}


def pasta_do_bot(fluxo):
    """evals/<bot>/fluxo/<fluxo> -> bots/<bot>. O <bot> pode ter mais de um nível (assessor/envio)."""
    partes = fluxo.relative_to(ROOT / "evals").parts
    if "fluxo" not in partes or partes.index("fluxo") == 0:
        sys.exit(f"{fluxo} nao esta em evals/<bot>/fluxo/<fluxo>")
    return ROOT / "bots" / Path(*partes[: partes.index("fluxo")])


def barra(caminho):
    return str(caminho).replace("\\", "/")


def montar(fluxo, dest):
    """Prepara a pasta de execução e devolve (pedido, prompt de sistema) do ator."""
    bot = pasta_do_bot(fluxo)
    cenario = secoes((fluxo / "cenario.md").read_text(encoding="utf-8"))
    perfil = secoes((bot / "bot.md").read_text(encoding="utf-8"))["Perfil"]
    shutil.copytree(bot / "skills", dest / ".claude" / "skills")
    for pasta in ("workspace", "tmp"):
        (dest / pasta).mkdir()
    trocas = {"{execucao}": barra(dest), "{repo}": barra(ROOT), "{python}": barra(sys.executable)}

    def preencher(texto):
        for chave, valor in trocas.items():
            texto = texto.replace(chave, valor)
        return texto

    return preencher(cenario["Pedido"]), preencher(f"{perfil}\n\n{cenario['Plataforma']}")


def comando_ator(claude, fluxo, sistema, skills):
    # setting-sources project tira as skills e as rules do usuário; o claudeMdExcludes tira o CLAUDE.md dele.
    excluir = {"claudeMdExcludes": [barra(Path.home() / ".claude" / "CLAUDE.md"), "**/CLAUDE.md"]}
    permitidas = [f for f in FERRAMENTAS if f != "Skill"] + [f"Skill({s})" for s in skills]
    comando = [
        claude, "-p", "--model", ATOR, "--setting-sources", "project", "--settings", json.dumps(excluir),
        "--strict-mcp-config", "--tools", ",".join(FERRAMENTAS), "--allowedTools", *permitidas,
        "--permission-mode", "dontAsk", "--append-system-prompt", sistema,
        "--output-format", "stream-json", "--verbose", "--forward-subagent-text", "--no-session-persistence",
    ]
    agentes = fluxo / "agentes.json"
    if agentes.is_file():
        comando[2:2] = ["--agents", str(agentes)]
    return comando


def cortar(texto, linha):
    if len(texto) <= LIMITE:
        return texto
    return f"{texto[:LIMITE]}\n\n[cortado: {LIMITE} de {len(texto)} caracteres; integra no transcript.jsonl, linha {linha}]"


def conteudo(bloco):
    """Texto de um tool_result, que vem como string ou como lista de blocos."""
    valor = bloco.get("content")
    if isinstance(valor, list):
        return "\n".join(b.get("text", f"[{b.get('type')}]") for b in valor)
    return valor or ""


def legivel(linhas):
    """Transcript em markdown a partir do stream-json do ator, um passo por bloco.

    Cada chamada de ferramenta ganha um número de passo. O resultado e as
    mensagens de subagente apontam para esse número, e bloco longo é cortado
    com a linha do jsonl onde está a íntegra.
    """
    saida = ["# Transcript do ator"]
    chamadas = {}  # tool_use_id -> (passo, nome)
    passo = 0
    for n, linha in enumerate(linhas, 1):
        if not linha.strip():
            continue
        evento = json.loads(linha)
        tipo = evento.get("type")
        if tipo == "system" and evento.get("subtype") == "init":
            saida.append(
                f"modelo: {evento.get('model')}\n\nferramentas: {', '.join(evento.get('tools', []))}\n\n"
                f"skills: {', '.join(evento.get('skills', []))}\n\nagentes: {', '.join(evento.get('agents', []))}"
            )
        elif tipo == "system" and evento.get("subtype") == "permission_denied":
            saida.append(f"## permissao negada\n\n{cortar(json.dumps(evento, ensure_ascii=False), n)}")
        elif tipo == "result":
            saida.append(
                f"## fim: {evento.get('subtype')}\n\nturnos: {evento.get('num_turns')}, "
                f"duracao: {evento.get('duration_ms')} ms\n\npermissoes negadas: "
                f"{json.dumps(evento.get('permission_denials', []), ensure_ascii=False)}\n\n"
                f"{cortar(evento.get('result') or '', n)}"
            )
        elif tipo in ("assistant", "user"):
            pai = evento.get("parent_tool_use_id")
            quem = "ator"
            if pai:
                p, nome = chamadas.get(pai, ("?", "?"))
                quem = f"subagente {nome} do passo {p}"
            for bloco in evento["message"].get("content", []):
                if isinstance(bloco, str):
                    bloco = {"type": "text", "text": bloco}
                b = bloco.get("type")
                if b == "tool_use":
                    passo += 1
                    entrada = bloco.get("input", {})
                    nome = entrada.get("subagent_type") or entrada.get("skill") or bloco["name"]
                    chamadas[bloco["id"]] = (passo, nome)
                    corpo = entrada["command"] if bloco["name"] == "Bash" and "command" in entrada else json.dumps(entrada, ensure_ascii=False, indent=1)
                    saida.append(f"## passo {passo}: {quem} chama {bloco['name']} ({nome})\n\n```\n{cortar(corpo, n)}\n```")
                elif b == "tool_result":
                    p, nome = chamadas.get(bloco.get("tool_use_id"), ("?", "?"))
                    erro = " (erro)" if bloco.get("is_error") else ""
                    saida.append(f"### resultado do passo {p} ({nome}){erro}, para {quem}\n\n```\n{cortar(conteudo(bloco), n)}\n```")
                elif b in ("text", "thinking"):
                    texto = bloco.get("text") or bloco.get("thinking") or ""
                    if not texto.strip():
                        continue
                    if tipo == "user":
                        rotulo = f"entrada para {quem}"
                    else:
                        rotulo = f"{'texto' if b == 'text' else 'raciocinio'} de {quem}"
                    saida.append(f"### {rotulo}\n\n{cortar(texto, n)}")
    return "\n\n".join(saida) + "\n"


def avaliar(claude, fluxo, dest):
    """Roda o avaliador-transcript e devolve o relatório que ele imprime."""
    bot = pasta_do_bot(fluxo)
    pedido = (
        f"Avalie o dry run gravado em {barra(dest)}.\n\n"
        f"- transcript legivel: {barra(dest / 'transcript.md')}\n"
        f"- stream original: {barra(dest / 'transcript.jsonl')}\n"
        f"- Page publicada pelo ator (pode nao existir): {barra(dest / 'page.md')}\n"
        f"- cenario: {barra(fluxo / 'cenario.md')}\n"
        f"- erros ja vistos: {barra(fluxo / 'erros.md')}\n"
        f"- skills e ficha do bot: {barra(bot / 'skills')} e {barra(bot / 'bot.md')}\n"
    )
    comando = [
        claude, "-p", "--agent", "avaliador-transcript", "--model", AVALIADOR, "--add-dir", str(dest),
        "--allowedTools", "Read", "Grep", "Glob", "--permission-mode", "dontAsk", "--no-session-persistence",
    ]
    r = subprocess.run(comando, cwd=ROOT, input=pedido, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0 or not r.stdout.strip():
        sys.exit(f"o avaliador falhou (exit {r.returncode}): {r.stderr.strip()[:2000]}")
    return r.stdout


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Dry run de um fluxo de bot com avaliacao do transcript.")
    p.add_argument("fluxo", help="pasta do fluxo, por exemplo evals/analista/fluxo/tese")
    p.add_argument("--saida", help="pasta nova, fora do repositorio (padrao: pasta temporaria)")
    a = p.parse_args()
    fluxo = Path(a.fluxo).resolve()
    if a.saida:
        dest = Path(a.saida).resolve()
        if dest.exists():
            sys.exit(f"{dest} ja existe: passe em --saida uma pasta nova")
        dest.mkdir(parents=True)
    else:
        dest = Path(tempfile.mkdtemp(prefix=f"dry-run-{fluxo.name}-"))
    # O repositório é público: transcript e relatório nunca ficam dentro dele.
    if dest == ROOT or ROOT in dest.parents:
        sys.exit(f"{dest} fica dentro do repositorio: use uma pasta de fora")
    claude = shutil.which("claude")
    if not claude:
        sys.exit("claude fora do PATH")
    pedido, sistema = montar(fluxo, dest)
    skills = sorted(d.name for d in (dest / ".claude" / "skills").iterdir())
    # Sem subagente em segundo plano: na plataforma, o Task devolve a resposta do subagente na própria chamada.
    ambiente = {**os.environ, "CLAUDE_CODE_DISABLE_BACKGROUND_TASKS": "1"}
    print(f"execucao: {dest}", flush=True)
    jsonl = dest / "transcript.jsonl"
    with open(jsonl, "w", encoding="utf-8") as saida, open(dest / "ator.err", "w", encoding="utf-8") as erros:
        r = subprocess.run(comando_ator(claude, fluxo, sistema, skills), cwd=dest, input=pedido, env=ambiente,
                           stdout=saida, stderr=erros, text=True, encoding="utf-8")
    linhas = jsonl.read_text(encoding="utf-8").splitlines()
    if not linhas:
        sys.exit(f"o ator nao gravou transcript (exit {r.returncode}); veja {dest / 'ator.err'}")
    (dest / "transcript.md").write_text(legivel(linhas), encoding="utf-8", newline="\n")
    print(f"ator: exit {r.returncode}, transcript em {dest / 'transcript.md'}", flush=True)
    (dest / "relatorio.md").write_text(avaliar(claude, fluxo, dest), encoding="utf-8", newline="\n")
    print(f"relatorio: {dest / 'relatorio.md'}")


if __name__ == "__main__":
    main()

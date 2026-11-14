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

Se o `.env` da raiz do repositório tiver a linha `ASSESSOR_EVALS_DADOS=<pasta>`,
a pasta de execução é copiada no fim da rodada para
`<pasta>/execucoes/<bot>/<data>-<fluxo>-dry-run`. O ator nunca roda dentro dela.

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
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATOR = "sonnet"
AVALIADOR = "opus"
FERRAMENTAS = ["Bash", "Read", "Write", "Edit", "Glob", "Grep", "WebSearch", "WebFetch", "Agent", "Skill"]
# Linha do .env da raiz com a pasta de dados privada, que recebe a cópia de cada rodada.
VAR_DADOS = "ASSESSOR_EVALS_DADOS"
# Caracteres de cada bloco no transcript legível. A íntegra fica no transcript.jsonl.
LIMITE = 4000


def secoes(texto):
    """Título de cada seção `## ` e o texto dela, sem o título."""
    partes = re.split(r"^## (.+)$", texto, flags=re.M)
    return {titulo.strip(): corpo.strip() for titulo, corpo in zip(partes[1::2], partes[2::2])}


def pasta_do_bot(fluxo):
    """evals/<bot>/fluxo/<fluxo> -> bots/<bot>. O <bot> pode ter mais de um nível (assessor/envio)."""
    try:
        partes = fluxo.relative_to(ROOT / "evals").parts
    except ValueError:
        partes = ()
    if "fluxo" not in partes or partes.index("fluxo") == 0:
        sys.exit(f"{fluxo} nao esta em evals/<bot>/fluxo/<fluxo>")
    return ROOT / "bots" / Path(*partes[: partes.index("fluxo")])


def secao(arquivo, titulo):
    """Texto da seção `## <titulo>` do arquivo. Para com mensagem se o arquivo ou a seção faltar."""
    if not arquivo.is_file():
        sys.exit(f"{arquivo} nao existe")
    texto = secoes(arquivo.read_text(encoding="utf-8")).get(titulo)
    if texto is None:
        sys.exit(f"{arquivo} sem a secao '## {titulo}'")
    return texto


def ler_fluxo(fluxo):
    """(pasta do bot, pedido, prompt de sistema) do ator, lidos antes de criar a pasta de execução."""
    bot = pasta_do_bot(fluxo)
    cenario = fluxo / "cenario.md"
    sistema = f"{secao(bot / 'bot.md', 'Perfil')}\n\n{secao(cenario, 'Plataforma')}"
    return bot, secao(cenario, "Pedido"), sistema


def barra(caminho):
    return str(caminho).replace("\\", "/")


def montar(bot, pedido, sistema, dest):
    """Prepara a pasta de execução e devolve o pedido e o prompt de sistema com os caminhos preenchidos."""
    shutil.copytree(bot / "skills", dest / ".claude" / "skills")
    for pasta in ("workspace", "tmp"):
        (dest / pasta).mkdir()
    # as_uri codifica espaço e acento, que o curl recusa crus num file:///.
    trocas = {"{execucao}": barra(dest), "{repo_url}": ROOT.as_uri(), "{python}": barra(sys.executable)}

    def preencher(texto):
        for chave, valor in trocas.items():
            texto = texto.replace(chave, valor)
        return texto

    return preencher(pedido), preencher(sistema)


def ambiente(**extra):
    """O ambiente de quem roda, sem a chave de API: com ela, o claude -p se autentica pela API e não pelo plano."""
    return {**{k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}, **extra}


def comando_ator(claude, fluxo, sistema, skills):
    # setting-sources project tira as skills e as rules do usuário; o claudeMdExcludes tira o CLAUDE.md dele.
    excluir = {"claudeMdExcludes": [barra(Path.home() / ".claude" / "CLAUDE.md"), "**/CLAUDE.md"]}
    permitidas = [f for f in FERRAMENTAS if f != "Skill"] + [f"Skill({s})" for s in skills]
    comando = [
        claude, "-p", "--model", ATOR, "--setting-sources", "project", "--settings", json.dumps(excluir),
        "--strict-mcp-config", "--tools", ",".join(FERRAMENTAS), "--allowedTools", *permitidas,
        "--permission-mode", "dontAsk", "--append-system-prompt-file", str(sistema),
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
        try:
            evento = json.loads(linha)
        except json.JSONDecodeError:
            # Aviso em texto no stdout ou última linha cortada: entra como está.
            saida.append(f"## linha {n} fora do JSON\n\n```\n{cortar(linha, n)}\n```")
            continue
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
            blocos = evento["message"].get("content", [])
            if isinstance(blocos, str):  # mensagem em texto puro, sem lista de blocos
                blocos = [{"type": "text", "text": blocos}]
            for bloco in blocos:
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
    r = subprocess.run(comando, cwd=ROOT, input=pedido, env=ambiente(), capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0 or not r.stdout.strip():
        sys.exit(f"o avaliador falhou (exit {r.returncode}): {r.stderr.strip()[:2000]}")
    return r.stdout


def pasta_de_dados(arquivo=ROOT / ".env"):
    """Pasta de dados privada (`ASSESSOR_EVALS_DADOS` no .env da raiz), ou None se a linha não existir.

    Caminho relativo vale a partir da pasta do .env, não de onde o script foi chamado.
    """
    if not arquivo.is_file():
        return None
    for linha in arquivo.read_text(encoding="utf-8").splitlines():
        chave, _, valor = linha.partition("=")
        if chave.strip() == VAR_DADOS and valor.strip():
            return (arquivo.parent / valor.strip().strip("\"'")).resolve()
    return None


def arquivar(dest, bot, fluxo, dados):
    """Copia a pasta de execução para <dados>/execucoes/<bot>/<data>-<fluxo>-dry-run e devolve o destino.

    Segunda rodada no mesmo dia ganha o sufixo -2, a terceira -3.
    """
    base = dados / "execucoes" / bot.relative_to(ROOT / "bots") / f"{date.today().isoformat()}-{fluxo.name}-dry-run"
    alvo, n = base, 1
    while alvo.exists():
        n += 1
        alvo = base.with_name(f"{base.name}-{n}")
    shutil.copytree(dest, alvo)
    return alvo


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Dry run de um fluxo de bot com avaliacao do transcript.")
    p.add_argument("fluxo", help="pasta do fluxo, por exemplo evals/analista/fluxo/tese")
    p.add_argument("--saida", help="pasta nova, fora do repositorio (padrao: pasta temporaria)")
    a = p.parse_args()
    fluxo = Path(a.fluxo).resolve()
    bot, pedido, sistema = ler_fluxo(fluxo)
    claude = shutil.which("claude")
    if not claude:
        sys.exit("claude fora do PATH")
    base = Path(a.saida).resolve() if a.saida else Path(tempfile.gettempdir()).resolve()
    # O repositório é público: transcript e relatório nunca ficam dentro dele.
    if base == ROOT or ROOT in base.parents:
        sys.exit(f"{base} fica dentro do repositorio: use uma pasta de fora")
    dados = pasta_de_dados()
    if dados and (not dados.is_dir() or dados == ROOT or ROOT in dados.parents):
        sys.exit(f"{VAR_DADOS} do .env ({dados}) tem que ser uma pasta que existe, fora do repositorio")
    if a.saida:
        if base.exists():
            sys.exit(f"{base} ja existe: passe em --saida uma pasta nova")
        base.mkdir(parents=True)
        dest = base
    else:
        dest = Path(tempfile.mkdtemp(prefix=f"dry-run-{fluxo.name}-", dir=base))
    pedido, sistema = montar(bot, pedido, sistema, dest)
    arquivo_sistema = dest / "sistema.md"
    arquivo_sistema.write_text(sistema, encoding="utf-8", newline="\n")
    skills = sorted(d.name for d in (dest / ".claude" / "skills").iterdir())
    print(f"execucao: {dest}", flush=True)
    jsonl = dest / "transcript.jsonl"
    with open(jsonl, "w", encoding="utf-8") as saida, open(dest / "ator.err", "w", encoding="utf-8") as erros:
        # Sem subagente em segundo plano: na plataforma, o Task devolve a resposta do subagente na própria chamada.
        r = subprocess.run(comando_ator(claude, fluxo, arquivo_sistema, skills), cwd=dest, input=pedido,
                           env=ambiente(CLAUDE_CODE_DISABLE_BACKGROUND_TASKS="1"),
                           stdout=saida, stderr=erros, text=True, encoding="utf-8")
    try:
        linhas = jsonl.read_text(encoding="utf-8").splitlines()
        if not linhas:
            sys.exit(f"o ator nao gravou transcript (exit {r.returncode}); veja {dest / 'ator.err'}")
        (dest / "transcript.md").write_text(legivel(linhas), encoding="utf-8", newline="\n")
        print(f"ator: exit {r.returncode}, transcript em {dest / 'transcript.md'}", flush=True)
        # Ator que caiu no meio deixa um fluxo truncado: um relatório sobre ele mediria a queda, não a skill.
        if r.returncode != 0:
            sys.exit(f"rodada incompleta: o ator saiu com exit {r.returncode}, sem avaliacao; veja {dest / 'ator.err'}")
        (dest / "relatorio.md").write_text(avaliar(claude, fluxo, dest), encoding="utf-8", newline="\n")
        print(f"relatorio: {dest / 'relatorio.md'}")
    finally:
        # A rodada que parou no meio também é copiada: o transcript dela explica a parada.
        if dados:
            try:
                print(f"copia: {arquivar(dest, bot, fluxo, dados)}", flush=True)
            except OSError as e:
                # Falha da cópia não esconde o motivo da parada da rodada, que sai logo depois.
                print(f"copia falhou ({e}); a rodada continua em {dest}", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()

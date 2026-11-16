#!/usr/bin/env python3
"""Dry run de um fluxo de bot: um ator faz o papel do bot e um avaliador lê o transcript.

O ator é um `claude -p` headless numa pasta de execução fora do repositório,
com as skills da branch em `.claude/skills/`, o `## Perfil` do `bot.md` e a
seção `## Plataforma` do cenário no prompt de sistema, e a seção `## Pedido`
como mensagem do dono. As instruções globais de quem roda (o CLAUDE.md e as
rules do usuário) ficam fora do contexto do ator.

Depois o agente `avaliador-transcript` lê o transcript contra as skills e o
`anti-patterns.md` do fluxo e escreve o relatório de desvios. Tudo fica na pasta de
execução: transcript.jsonl (o stream do ator), transcript.md (a versão
legível), page.md (se o ator publicou), page.html (o page.md renderizado, só para
leitura) e relatorio.md.

Um fluxo tem um `cenario.md`, ou vários cenários em `cenarios/<nome>.md` com o
`## Plataforma` comum num `plataforma.md`. Com vários, `--cenario NOME` roda um e
`--all` roda todos em paralelo, cada um em `<execucao>/<nome>`.

Se o `.env` da raiz do repositório tiver a linha `ASSESSOR_EVALS_DADOS=<pasta>`,
a pasta de execução é copiada no fim da rodada para
`<pasta>/execucoes/<bot>/<data>-<fluxo>[-<cenario>]-dry-run`. O ator nunca roda dentro dela.

Com `--variantes`, o script roda o eixo de gosto sobre um cenário de
`evals/<bot>/gosto/<pergunta>/`: cada variante de `variantes/<nome>/` (só os
arquivos que mudam em `bots/<bot>/`, `bot.md` ou `skills/<skill>/...`) é
sobreposta à cópia do bot, e o ator roda M vezes com cada uma, sem avaliador.
Cada amostra tem a sua pasta de execução, `<variante>-<n>`, dentro da pasta da
rodada, que ganha um `index.html` com o link da `page.html` de cada amostra.
Com `--partida`, a pasta dada (os arquivos congelados que o cenário manda usar,
só em `tmp/` e `workspace/`) é copiada sobre cada pasta de execução antes de o
ator rodar. A pasta da rodada
é copiada para `<pasta>/execucoes/<bot>/<data>-<pergunta>-gosto`.

O ator usa o modelo de `--modelo` (padrão: sonnet). Com `--rodadas N`, o modo de fluxo
roda N vezes, cada rodada (ator e avaliador) na sua pasta de execução, `rodada-<n>`,
dentro da pasta da execução, e imprime no fim a tabela de métricas das rodadas.

Com `--metricas PASTA ...`, o script não roda nada: lê cada transcript.jsonl guardado
nas pastas (em qualquer nível, todas do mesmo fluxo) e imprime a tabela de métricas, uma linha por modelo do
ator, com a mediana e a faixa de cada métrica, e as requisições e os tokens separados por
modelo usado na rodada.

Roda pelo login do plano do Claude Code, sem chave de API.

Uso:
  python scripts/dry-run.py evals/<bot>/fluxo/<fluxo> [--modelo MODELO] [--rodadas N] [--saida PASTA]
  python scripts/dry-run.py evals/analista-v2/fluxo/tese (--cenario NOME | --all) [--modelo MODELO] [--rodadas N] [--saida PASTA]
  python scripts/dry-run.py evals/<bot>/gosto/<pergunta> --variantes [NOME ...] [--amostras M] [--partida PASTA] [--modelo MODELO] [--saida PASTA]
  python scripts/dry-run.py --metricas PASTA [PASTA ...]
"""
import argparse
import html
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATOR = "sonnet"
AVALIADOR = "opus"
FERRAMENTAS = ["Bash", "Read", "Write", "Edit", "Glob", "Grep", "WebSearch", "WebFetch", "Agent", "Skill"]
# Skills do Claude Code que o disableBundledSkills deixa no init; o skillOverrides "off" tira por nome.
# Skill nova numa versão futura escapa desta lista e aparece na seção "## fora do bot" do transcript.md.
ESCONDIDAS = ["design", "doctor", "plugin-authoring"]
# Linha do .env da raiz com a pasta de dados privada, que recebe a cópia de cada rodada.
VAR_DADOS = "ASSESSOR_EVALS_DADOS"
# Teto de cenários rodando juntos com --all: cada um tem um ator e um avaliador próprios.
PARALELO = 4
# Caracteres de cada bloco no transcript legível. A íntegra fica no transcript.jsonl.
LIMITE = 4000


def secoes(texto):
    """Título de cada seção `## ` e o texto dela, sem o título."""
    partes = re.split(r"^## (.+)$", texto, flags=re.M)
    return {titulo.strip(): corpo.strip() for titulo, corpo in zip(partes[1::2], partes[2::2])}


def pasta_do_bot(fluxo):
    """evals/<bot>/fluxo/<fluxo> ou evals/<bot>/gosto/<pergunta> -> bots/<bot>. O <bot> pode ter mais de um nível (assessor/envio)."""
    try:
        partes = fluxo.relative_to(ROOT / "evals").parts
    except ValueError:
        partes = ()
    eixo = next((i for i, parte in enumerate(partes) if parte in ("fluxo", "gosto")), 0)
    if eixo == 0:
        sys.exit(f"{fluxo} nao esta em evals/<bot>/fluxo/<fluxo> nem em evals/<bot>/gosto/<pergunta>")
    return ROOT / "bots" / Path(*partes[:eixo])


def secao(arquivo, titulo):
    """Texto da seção `## <titulo>` do arquivo. Para com mensagem se o arquivo ou a seção faltar."""
    if not arquivo.is_file():
        sys.exit(f"{arquivo} nao existe")
    texto = secoes(arquivo.read_text(encoding="utf-8")).get(titulo)
    if texto is None:
        sys.exit(f"{arquivo} sem a secao '## {titulo}'")
    return texto


def cenarios(fluxo):
    """{nome: arquivo} dos cenários do fluxo: um por `.md` de `cenarios/`, ou o `cenario.md` sozinho, de nome vazio."""
    pasta = fluxo / "cenarios"
    # Fluxo com as duas formas ao mesmo tempo teria um arquivo ignorado em silêncio.
    if pasta.is_dir() and (fluxo / "cenario.md").is_file():
        sys.exit(f"{fluxo} tem cenarios/ e cenario.md: passe o cenario.md para cenarios/ ou tire cenarios/")
    if not pasta.is_dir():
        if (fluxo / "plataforma.md").is_file():
            sys.exit(f"{fluxo} tem plataforma.md sem cenarios/: o ## Plataforma vai no cenario.md")
        return {"": fluxo / "cenario.md"}
    achados = {f.stem: f for f in sorted(pasta.glob("*.md"))}
    if not achados:
        sys.exit(f"{pasta} sem cenario")
    return achados


def ler_fluxo(fluxo, variante=None, cenario=None):
    """(pasta do bot, pedido, prompt de sistema) do ator, lidos antes de criar a pasta de execução.

    O `## Perfil` vem do `bot.md` da variante, se ela tiver um, e do bot se não tiver. O `## Plataforma`
    vem do `plataforma.md` do fluxo, que vale para todos os cenários de `cenarios/`, ou do próprio cenário.
    """
    bot = pasta_do_bot(fluxo)
    ficha = variante / "bot.md" if variante and (variante / "bot.md").is_file() else bot / "bot.md"
    cenario = cenario or fluxo / "cenario.md"
    plataforma = fluxo / "plataforma.md" if (fluxo / "plataforma.md").is_file() else cenario
    sistema = f"{secao(ficha, 'Perfil')}\n\n{secao(plataforma, 'Plataforma')}"
    return bot, secao(cenario, "Pedido"), sistema


def arquivos_da_variante(variante, bot):
    """Arquivos da variante, relativos a ela. Para com mensagem se algum não sobrepõe nada no bot.

    Vale `bot.md` ou um arquivo que o bot já tem em `skills/`, com o nome igual, maiúsculas
    inclusive: nome errado viraria arquivo novo em silêncio, e a variante rodaria igual ao bot.
    O `.gitkeep`, que guarda no git a variante vazia, fica de fora.
    """
    if not variante.is_dir():
        sys.exit(f"variante {variante} nao existe")
    # Comparação por texto: no Windows, Path compara sem distinguir maiúsculas.
    existentes = {"bot.md"} | {p.relative_to(bot).as_posix() for p in (bot / "skills").rglob("*") if p.is_file()}
    arquivos = [p.relative_to(variante) for p in sorted(variante.rglob("*")) if p.is_file() and p.name != ".gitkeep"]
    for rel in arquivos:
        if rel.as_posix() not in existentes:
            sys.exit(f"{variante / rel}: a variante so sobrepoe bot.md ou um arquivo que o bot ja tem em skills/")
    return arquivos


def ler_partida(partida):
    """A pasta de --partida, conferida antes de qualquer amostra rodar.

    Ela só traz a entrada do ator, `tmp/` e `workspace/`: qualquer outra coisa (o `.claude/` de uma
    rodada anterior passada inteira) regravaria as skills por cima da variante em toda amostra.
    """
    if not partida.is_dir():
        sys.exit(f"--partida {partida} nao e uma pasta")
    sobra = sorted(p.name for p in partida.iterdir() if p.name not in ("tmp", "workspace") or not p.is_dir())
    if sobra:
        sys.exit(f"--partida {partida} so pode ter as pastas tmp/ e workspace/; tire: {', '.join(sobra)}")
    return partida


def barra(caminho):
    return str(caminho).replace("\\", "/")


def montar(bot, pedido, sistema, dest, variante=None, partida=None):
    """Prepara a pasta de execução e devolve o pedido e o prompt de sistema com os caminhos preenchidos.

    Os arquivos de `skills/` da variante substituem os da cópia do bot. A pasta de partida, já
    conferida por `ler_partida`, traz só `tmp/` e `workspace/` e é copiada por cima delas.
    """
    shutil.copytree(bot / "skills", dest / ".claude" / "skills")
    for rel in arquivos_da_variante(variante, bot) if variante else []:
        if rel.parts[0] == "skills":
            shutil.copy2(variante / rel, dest / ".claude" / rel)
    for pasta in ("workspace", "tmp"):
        (dest / pasta).mkdir()
    if partida:
        shutil.copytree(partida, dest, dirs_exist_ok=True)
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


def comando_ator(claude, fluxo, sistema, skills, modelo):
    # setting-sources project tira as skills e as rules do usuário; o claudeMdExcludes tira o CLAUDE.md dele.
    # O disableBundledSkills e o skillOverrides tiram as skills do Claude Code: o allowedTools só
    # pré-aprova, e o dontAsk não nega skill que não pede aprovação.
    excluir = {
        "claudeMdExcludes": [barra(Path.home() / ".claude" / "CLAUDE.md"), "**/CLAUDE.md"],
        "disableBundledSkills": True,
        "skillOverrides": {s: "off" for s in ESCONDIDAS},
    }
    permitidas = [f for f in FERRAMENTAS if f != "Skill"] + [f"Skill({s})" for s in skills]
    comando = [
        claude, "-p", "--model", modelo, "--setting-sources", "project", "--settings", json.dumps(excluir),
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


def legivel(linhas, do_bot):
    """Transcript em markdown a partir do stream-json do ator, um passo por bloco.

    Cada chamada de ferramenta ganha um número de passo. O resultado e as
    mensagens de subagente apontam para esse número, e bloco longo é cortado
    com a linha do jsonl onde está a íntegra.

    Skill que não está em `do_bot` (as pastas de `.claude/skills` da execução), listada
    no init ou chamada pela ferramenta Skill, entra na seção `## fora do bot`, logo
    abaixo do título. A chamada é comparada pelo nome pedido, e não pela lista do
    init: uma skill do Claude Code pode carregar sem aparecer nele. A chamada cujo
    resultado veio com erro leva `recusada`: houve tentativa, não carga.
    """
    saida = ["# Transcript do ator"]
    chamadas = {}  # tool_use_id -> (passo, nome)
    passo = 0
    vistas_fora, chamadas_fora = [], {}  # tool_use_id -> texto da chamada de skill de fora do bot
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
            vistas_fora = [s for s in evento.get("skills", []) if s not in do_bot]
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
                    fora = ""
                    if bloco["name"] == "Skill" and entrada.get("skill") not in do_bot:
                        fora = " [fora do bot]"
                        chamadas_fora[bloco["id"]] = f"{entrada.get('skill')} (passo {passo}, {quem}"
                    corpo = entrada["command"] if bloco["name"] == "Bash" and "command" in entrada else json.dumps(entrada, ensure_ascii=False, indent=1)
                    saida.append(f"## passo {passo}: {quem} chama {bloco['name']} ({nome}){fora}\n\n```\n{cortar(corpo, n)}\n```")
                elif b == "tool_result":
                    p, nome = chamadas.get(bloco.get("tool_use_id"), ("?", "?"))
                    erro = " (erro)" if bloco.get("is_error") else ""
                    if erro and bloco.get("tool_use_id") in chamadas_fora:
                        chamadas_fora[bloco["tool_use_id"]] += ", recusada"
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
    if vistas_fora or chamadas_fora:
        saida.insert(1, f"## fora do bot\n\nno init: {', '.join(vistas_fora) or 'nenhuma'}\n\n"
                        f"chamadas: {'; '.join(c + ')' for c in chamadas_fora.values()) or 'nenhuma'}")
    return "\n\n".join(saida) + "\n"


# (chave, rótulo) das métricas da rodada e das métricas de cada modelo, na ordem das colunas.
DA_RODADA = [("turnos", "turnos"), ("minutos", "minutos")]
DO_MODELO = [
    ("requisicoes", "requisicoes no stream"), ("entrada", "entrada"), ("cache_lido", "cache lido"),
    ("cache_gravado", "cache gravado"), ("saida", "saida"),
]
# Campo do `modelUsage` do `result` de cada métrica de tokens.
USO = {"entrada": "inputTokens", "cache_lido": "cacheReadInputTokens",
       "cache_gravado": "cacheCreationInputTokens", "saida": "outputTokens"}


def metricas(linhas):
    """Métricas de uma rodada a partir do stream-json do ator, ou None se o stream não tem um `result` de sucesso.

    Sem o evento `result`, ou com ele marcado como erro (`subtype` diferente de `success`, ou
    `is_error`), a rodada foi cortada e os números dela são de um fluxo truncado.

    Devolve o modelo do ator (do `init`), os turnos e os minutos da rodada e, em `modelos`, as
    requisições e os tokens de cada modelo que a rodada usou. Requisições são as mensagens distintas
    (o `message.id`) do ator e dos subagentes, pelo `model` de cada mensagem: uma resposta com vários
    blocos chega em vários eventos com o mesmo id. A ferramenta que chama um modelo por dentro (o
    WebFetch resume a página com o Haiku) não emite mensagem: o modelo dela tem tokens e zero
    requisições no stream. Os tokens vêm do `modelUsage` do `result`, que traz cada modelo com os
    subagentes e essas chamadas internas. O `usage` de cada evento não serve: o de saída é parcial.
    Os turnos são o `num_turns` do `result`, que conta cada resultado de ferramenta do ator.
    """
    ator, mensagens, fim = "?", {}, None
    for linha in linhas:
        try:
            evento = json.loads(linha)
        except json.JSONDecodeError:
            continue
        if not isinstance(evento, dict):
            continue
        tipo = evento.get("type")
        if tipo == "system" and evento.get("subtype") == "init":
            ator = evento.get("model") or "?"
        elif tipo == "assistant" and isinstance(evento.get("message"), dict):
            m = evento["message"]
            mensagens[(evento.get("parent_tool_use_id"), m.get("id"))] = m.get("model") or "?"
        elif tipo == "result":
            fim = evento
    if fim is None or fim.get("subtype") != "success" or fim.get("is_error"):
        return None
    uso = fim.get("modelUsage", {})
    modelos = {}
    for modelo in set(uso) | set(mensagens.values()):
        modelos[modelo] = {chave: uso.get(modelo, {}).get(campo, 0) for chave, campo in USO.items()}
        modelos[modelo]["requisicoes"] = sum(1 for m in mensagens.values() if m == modelo)
    return {"ator": ator, "turnos": fim.get("num_turns", 0), "minutos": fim.get("duration_ms", 0) / 60000,
            "modelos": modelos}


def numero(valor):
    """1234 -> 1.234 e 4.26 -> 4,3: milhar com ponto, uma casa decimal com vírgula se não for inteiro."""
    texto = f"{valor:,.0f}" if valor == int(valor) else f"{valor:,.1f}"
    return texto.translate(str.maketrans(",.", ".,"))


def faixa(valores):
    """Mediana dos valores e, se eles diferem, o mínimo e o máximo entre parênteses."""
    texto = numero(statistics.median(valores))
    if min(valores) != max(valores):
        texto += f" ({numero(min(valores))} a {numero(max(valores))})"
    return texto


def tabela(pastas):
    """Tabelas em markdown das rodadas guardadas nas pastas, com a mediana e a faixa de cada métrica.

    A primeira tem uma linha por modelo do ator (turnos e minutos da rodada). A segunda tem uma
    linha por modelo do ator e modelo usado na rodada (requisições e tokens só daquele modelo); a
    rodada que não usou o modelo entra com zero. Cada transcript.jsonl das pastas, em qualquer
    nível, é uma rodada. A que não tem um `result` de sucesso (ator que caiu no meio) fica fora,
    com aviso no stderr. Devolve "" sem rodada completa. As pastas têm que ser do mesmo fluxo:
    a tabela agrupa só pelo modelo do ator.
    """
    por_ator = {}
    for pasta in pastas:
        for jsonl in sorted(Path(pasta).rglob("transcript.jsonl")):
            m = metricas(jsonl.read_text(encoding="utf-8").splitlines())
            if m is None:
                print(f"sem result de sucesso, fora da tabela: {jsonl}", file=sys.stderr, flush=True)
                continue
            por_ator.setdefault(m["ator"], []).append(m)
    if not por_ator:
        return ""

    def cabecalho(*colunas):
        return [f"| {' | '.join(colunas)} |", "|" + " --- |" * len(colunas)]

    rodada = cabecalho("ator", "rodadas", *(r for _, r in DA_RODADA))
    modelo = cabecalho("ator", "modelo", *(r for _, r in DO_MODELO))
    for ator, rodadas in sorted(por_ator.items()):
        rodada.append(f"| {ator} | {len(rodadas)} | " + " | ".join(faixa([r[c] for r in rodadas]) for c, _ in DA_RODADA) + " |")
        for usado in sorted({u for r in rodadas for u in r["modelos"]}):
            celulas = (faixa([r["modelos"].get(usado, {}).get(c, 0) for r in rodadas]) for c, _ in DO_MODELO)
            modelo.append(f"| {ator} | {usado} | " + " | ".join(celulas) + " |")
    return "\n".join(rodada) + "\n\n" + "\n".join(modelo) + "\n"


def avaliar(claude, fluxo, dest, live=False, cenario=None):
    """Roda o avaliador-transcript e devolve o relatório que ele imprime. Levanta RuntimeError se ele falha.

    No live run (`scripts/live-run.py`) não há stream do ator nem cenário: o pedido é a mensagem do dono no transcript.
    """
    bot = pasta_do_bot(fluxo)
    plataforma = fluxo / "plataforma.md"
    do_dry_run = (
        f"- stream original: {barra(dest / 'transcript.jsonl')}\n"
        f"- Page publicada pelo ator (pode nao existir): {barra(dest / 'page.md')}\n"
        f"- cenario: {barra(cenario or fluxo / 'cenario.md')}\n"
        + (f"- plataforma do fluxo, comum a todos os cenarios: {barra(plataforma)}\n" if plataforma.is_file() else "")
    )
    pedido = (
        f"Avalie o {'live run' if live else 'dry run'} gravado em {barra(dest)}.\n\n"
        f"- transcript legivel: {barra(dest / 'transcript.md')}\n"
        + (f"- Page publicada pelo bot (pode nao existir): {barra(dest / 'page.md')}\n" if live else do_dry_run)
        + f"- anti-patterns: {barra(fluxo / 'anti-patterns.md')}\n"
        f"- skills e ficha do bot: {barra(bot / 'skills')} e {barra(bot / 'bot.md')}\n"
    )
    comando = [
        claude, "-p", "--agent", "avaliador-transcript", "--model", AVALIADOR, "--add-dir", str(dest),
        "--allowedTools", "Read", "Grep", "Glob", "--permission-mode", "dontAsk", "--no-session-persistence",
    ]
    r = subprocess.run(comando, cwd=ROOT, input=pedido, env=ambiente(), capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0 or not r.stdout.strip():
        raise RuntimeError(f"o avaliador falhou (exit {r.returncode}): {r.stderr.strip()[:2000]}")
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


def arquivar(dest, bot, fluxo, dados, sufixo="dry-run", cenario=""):
    """Copia a pasta de execução para <dados>/execucoes/<bot>/<data>-<fluxo>[-<cenario>]-<sufixo> e devolve o destino.

    Segunda rodada no mesmo dia ganha o sufixo -2, a terceira -3.
    """
    nome = f"{fluxo.name}-{cenario}" if cenario else fluxo.name
    base = dados / "execucoes" / bot.relative_to(ROOT / "bots") / f"{date.today().isoformat()}-{nome}-{sufixo}"
    alvo, n = base, 1
    while alvo.exists():
        n += 1
        alvo = base.with_name(f"{base.name}-{n}")
    shutil.copytree(dest, alvo)
    return alvo


def guardar(dest, bot, fluxo, dados, sufixo="dry-run", cenario=""):
    """Copia a rodada para a pasta de dados, se houver uma, e devolve o destino (None sem cópia)."""
    if not dados:
        return None
    try:
        alvo = arquivar(dest, bot, fluxo, dados, sufixo, cenario)
    except OSError as e:
        # Falha da cópia não esconde o motivo da parada da rodada, que sai logo depois.
        print(f"copia falhou ({e}); a rodada continua em {dest}", file=sys.stderr, flush=True)
        return None
    print(f"copia: {alvo}", flush=True)
    return alvo


def atuar(claude, fluxo, pedido, sistema, dest, modelo):
    """Roda o ator na pasta de execução montada e devolve o exit dele.

    Grava sistema.md, transcript.jsonl e ator.err e, se o ator gravou algum evento, transcript.md.
    """
    arquivo_sistema = dest / "sistema.md"
    arquivo_sistema.write_text(sistema, encoding="utf-8", newline="\n")
    skills = sorted(d.name for d in (dest / ".claude" / "skills").iterdir())
    jsonl = dest / "transcript.jsonl"
    with open(jsonl, "w", encoding="utf-8") as saida, open(dest / "ator.err", "w", encoding="utf-8") as erros:
        # Sem subagente em segundo plano: na plataforma, o Task devolve a resposta do subagente na própria chamada.
        r = subprocess.run(comando_ator(claude, fluxo, arquivo_sistema, skills, modelo), cwd=dest, input=pedido,
                           env=ambiente(CLAUDE_CODE_DISABLE_BACKGROUND_TASKS="1"),
                           stdout=saida, stderr=erros, text=True, encoding="utf-8")
    linhas = jsonl.read_text(encoding="utf-8").splitlines()
    if linhas:
        (dest / "transcript.md").write_text(legivel(linhas, skills), encoding="utf-8", newline="\n")
    return r.returncode


def indice(rodada, titulo, feitas):
    """Grava o index.html da rodada: uma linha por variante, uma coluna por amostra, com o link da page.html.

    Amostra cujo transcript.md tem a seção `## fora do bot` leva na célula as skills de fora do bot.
    """
    linhas = {}
    for variante, n, codigo, segundos in feitas:
        nome = html.escape(f"{variante}-{n}")
        celula = f'<a href="{nome}/page.html">{nome}</a>' if (rodada / f"{variante}-{n}" / "page.html").is_file() else f"{nome}: sem page.html"
        if codigo != 0:
            celula += f" (exit {codigo})"
        # Sem transcript.md o ator não emitiu nada, e o ator.err é o que explica a queda.
        transcript = rodada / f"{variante}-{n}" / "transcript.md"
        log = "transcript.md" if transcript.is_file() else "ator.err"
        celula += f' <small>{segundos:.0f} s, <a href="{nome}/{log}">{log}</a></small>'
        fora = transcript.is_file() and re.search(r"^## fora do bot\n\nno init: (.*)\n\nchamadas: (.*)$",
                                                  transcript.read_text(encoding="utf-8"), re.M)
        if fora:
            celula += f"<br><strong>fora do bot: chamadas {html.escape(fora[2])}; no init {html.escape(fora[1])}</strong>"
        linhas.setdefault(variante, []).append(f"<td>{celula}</td>")
    corpo = "\n".join(f"<tr><th>{html.escape(v)}</th>{''.join(c)}</tr>" for v, c in linhas.items())
    t = html.escape(titulo)
    (rodada / "index.html").write_text(
        f'<!doctype html>\n<meta charset="utf-8">\n<title>{t}</title>\n<h1>{t}</h1>\n<table>\n{corpo}\n</table>\n',
        encoding="utf-8", newline="\n",
    )


def gosto(claude, fluxo, bot, variantes, amostras, partida, rodada, modelo):
    """Roda M amostras de cada variante, cada uma em <rodada>/<variante>-<n>, e devolve (variante, n, exit, segundos).

    O index.html é regravado depois de cada amostra, para a rodada interrompida ainda abrir o que saiu.
    """
    feitas = []
    for n in range(1, amostras + 1):
        # Uma amostra de cada variante por volta: a rodada que parar no meio ainda compara todas.
        for nome, variante, pedido, sistema in variantes:
            dest = rodada / f"{nome}-{n}"
            dest.mkdir()
            ped, sis = montar(bot, pedido, sistema, dest, variante, partida)
            print(f"amostra: {dest}", flush=True)
            inicio = time.monotonic()
            codigo = atuar(claude, fluxo, ped, sis, dest, modelo)
            feitas.append((nome, n, codigo, time.monotonic() - inicio))
            indice(rodada, fluxo.name, feitas)
            pagina = "sim" if (dest / "page.html").is_file() else "nao"
            print(f"  exit {codigo}, {feitas[-1][3]:.0f} s, page.html: {pagina}", flush=True)
    return feitas


def ler_variantes(fluxo, bot, nomes):
    """(nome, pasta, pedido, prompt de sistema) de cada variante, conferidas antes de qualquer amostra rodar.

    Sem nomes, valem todas as pastas de <cenario>/variantes/.
    """
    pasta = fluxo / "variantes"
    if not pasta.is_dir():
        sys.exit(f"{fluxo} sem a pasta variantes/")
    nomes = nomes or sorted(d.name for d in pasta.iterdir() if d.is_dir())
    if not nomes:
        sys.exit(f"{pasta} sem variante")
    repetidas = sorted({n for n in nomes if nomes.count(n) > 1})
    if repetidas:
        sys.exit(f"variante repetida em --variantes: {', '.join(repetidas)}")
    variantes = []
    for nome in nomes:
        arquivos_da_variante(pasta / nome, bot)
        _, pedido, sistema = ler_fluxo(fluxo, pasta / nome)
        variantes.append((nome, pasta / nome, pedido, sistema))
    return variantes


def pagina_html(pasta):
    """Grava page.html a partir do page.md do ator, só para leitura: o avaliador lê o page.md."""
    try:
        import markdown
    except ImportError:
        # A cópia é só para leitura: sem o pacote, a rodada segue sem ela.
        print(f"sem o pacote markdown: {pasta} fica sem page.html", file=sys.stderr, flush=True)
        return
    md = pasta / "page.md"
    if md.is_file():
        corpo = markdown.markdown(md.read_text(encoding="utf-8"), extensions=["tables"])
        (pasta / "page.html").write_text(f'<!doctype html>\n<meta charset="utf-8">\n<title>Page</title>\n{corpo}\n',
                                         encoding="utf-8", newline="\n")


def rodar_cenario(claude, fluxo, bot, nome, arquivo, pedido, sistema, dest, rodadas, modelo, dados, paralelo=False):
    """Roda as rodadas (ator e avaliador) de um cenário em dest e devolve as mensagens das rodadas incompletas.

    Em paralelo, cada linha impressa começa com `[<nome>]`. A cópia na pasta de dados leva o nome do cenário sempre.
    """
    marca = f"[{nome}] " if paralelo else ""

    def log(texto):
        print(f"{marca}{texto}", flush=True)

    # Uma rodada fica na própria pasta de execução; com mais de uma, cada uma tem a sua dentro dela.
    pastas = [dest] if rodadas == 1 else [dest / f"rodada-{n}" for n in range(1, rodadas + 1)]
    incompletas = []
    try:
        for pasta in pastas:
            pasta.mkdir(parents=True, exist_ok=True)
            ped, sis = montar(bot, pedido, sistema, pasta)
            log(f"execucao: {pasta}")
            codigo = atuar(claude, fluxo, ped, sis, pasta, modelo)
            pagina_html(pasta)
            if not (pasta / "transcript.md").is_file():
                incompletas.append(f"o ator nao gravou transcript (exit {codigo}); veja {pasta / 'ator.err'}")
                continue
            log(f"ator: exit {codigo}, transcript em {pasta / 'transcript.md'}")
            # Ator que caiu no meio deixa um fluxo truncado: um relatório sobre ele mediria a queda, não a skill.
            if codigo != 0:
                incompletas.append(f"rodada incompleta: o ator saiu com exit {codigo}, sem avaliacao; veja {pasta / 'ator.err'}")
                continue
            try:
                relatorio = avaliar(claude, fluxo, pasta, cenario=arquivo)
            except RuntimeError as e:
                incompletas.append(f"{e}; rodada em {pasta}")
                continue
            (pasta / "relatorio.md").write_text(relatorio, encoding="utf-8", newline="\n")
            log(f"relatorio: {pasta / 'relatorio.md'}")
    finally:
        # A rodada que parou no meio também é copiada: o transcript dela explica a parada.
        guardar(dest, bot, fluxo, dados, cenario=nome)
    return [f"{marca}{m}" for m in incompletas]


def escolher_cenarios(fluxo, nome, todos):
    """{nome: arquivo} dos cenários que a rodada usa: o de --cenario, todos com --all, ou o único que houver."""
    disponiveis = cenarios(fluxo)
    lista = ", ".join(disponiveis)
    if todos and nome:
        sys.exit("passe --cenario ou --all, nao os dois")
    if todos:
        return disponiveis
    if nome:
        if nome not in disponiveis:
            sys.exit(f"cenario '{nome}' nao existe em {fluxo / 'cenarios'}; ha: {lista}")
        return {nome: disponiveis[nome]}
    if len(disponiveis) > 1:
        sys.exit(f"{fluxo} tem varios cenarios: passe --cenario NOME ou --all (ha: {lista})")
    return disponiveis


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Dry run de um fluxo de bot com avaliacao do transcript, ou amostras de gosto.")
    p.add_argument("fluxo", nargs="?",
                   help="pasta do cenario: evals/<bot>/fluxo/<fluxo>, ou evals/<bot>/gosto/<pergunta> com --variantes")
    p.add_argument("--saida", help="pasta nova, fora do repositorio (padrao: pasta temporaria)")
    p.add_argument("--variantes", nargs="*", metavar="NOME",
                   help="gosto: variantes de <cenario>/variantes/ (so a opcao: todas); sem avaliador")
    p.add_argument("--amostras", type=int, default=1, help="gosto: amostras de cada variante (padrao: 1)")
    p.add_argument("--partida", help="gosto: pasta copiada sobre cada pasta de execucao antes do ator (arquivos congelados)")
    p.add_argument("--modelo", default=ATOR, help=f"modelo do ator (padrao: {ATOR})")
    p.add_argument("--rodadas", type=int, default=1, help="fluxo: rodadas do ator e do avaliador, cada uma em rodada-<n> (padrao: 1)")
    p.add_argument("--cenario", metavar="NOME", help="fluxo: o cenario <fluxo>/cenarios/NOME.md")
    p.add_argument("--all", dest="todos", action="store_true",
                   help=f"fluxo: todos os cenarios de <fluxo>/cenarios/, ate {PARALELO} em paralelo, cada um em <execucao>/<nome>")
    p.add_argument("--metricas", nargs="+", metavar="PASTA",
                   help="so le: tabela de metricas dos transcript.jsonl guardados nas pastas, sem rodar nada")
    a = p.parse_args()
    if a.metricas:
        if a.fluxo:
            p.error("--metricas nao roda cenario: tire a pasta do cenario")
        faltam = [pasta for pasta in a.metricas if not Path(pasta).is_dir()]
        if faltam:
            sys.exit(f"pasta de --metricas que nao existe: {', '.join(faltam)}")
        texto = tabela(a.metricas)
        if not texto:
            sys.exit(f"nenhuma rodada com result de sucesso em {', '.join(a.metricas)}")
        print(texto, end="")
        return
    if not a.fluxo:
        p.error("passe a pasta do cenario, ou --metricas")
    fluxo = Path(a.fluxo).resolve()
    if a.variantes is None:
        if (fluxo / "variantes").is_dir():
            sys.exit(f"{fluxo} tem variantes/: passe --variantes")
        if a.partida or a.amostras != 1:
            sys.exit("--amostras e --partida so valem com --variantes")
        if a.rodadas < 1:
            sys.exit("--rodadas tem que ser 1 ou mais")
        # Todos os cenários são lidos antes de qualquer ator rodar: seção faltando para a execução inteira.
        lidos = {nome: (arquivo, *ler_fluxo(fluxo, cenario=arquivo))
                 for nome, arquivo in escolher_cenarios(fluxo, a.cenario, a.todos).items()}
        bot = pasta_do_bot(fluxo)
    else:
        if a.cenario or a.todos:
            sys.exit("--cenario e --all so valem no modo de fluxo")
        bot = pasta_do_bot(fluxo)
        variantes = ler_variantes(fluxo, bot, a.variantes)
        if a.rodadas != 1:
            sys.exit("--rodadas so vale no modo de fluxo; no gosto, use --amostras")
        if a.amostras < 1:
            sys.exit("--amostras tem que ser 1 ou mais")
        partida = ler_partida(Path(a.partida).resolve()) if a.partida else None
        # Cenário que parte de arquivos congelados tem a seção ## Partida: sem eles, o ator não tem de onde escrever.
        if not partida and "Partida" in secoes((fluxo / "cenario.md").read_text(encoding="utf-8")):
            sys.exit(f"{fluxo / 'cenario.md'} tem '## Partida': passe --partida com os arquivos congelados")
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
        prefixo = "gosto" if a.variantes is not None else "dry-run"
        sozinho = a.variantes is None and len(lidos) == 1 and next(iter(lidos))
        nome = f"{fluxo.name}-{sozinho}" if sozinho else fluxo.name
        dest = Path(tempfile.mkdtemp(prefix=f"{prefixo}-{nome}-", dir=base))

    if a.variantes is not None:
        print(f"rodada: {dest}", flush=True)
        try:
            feitas = gosto(claude, fluxo, bot, variantes, a.amostras, partida, dest, a.modelo)
        finally:
            alvo = guardar(dest, bot, fluxo, dados, "gosto")
        print(f"indice: {(alvo or dest) / 'index.html'}")
        falhas = [f"{v}-{n}" for v, n, codigo, _ in feitas if codigo != 0 or not (dest / f"{v}-{n}" / "page.html").is_file()]
        if falhas:
            sys.exit(f"amostras com exit diferente de zero ou sem page.html: {', '.join(falhas)}")
        return

    # Um cenário roda na pasta da execução; com mais de um, cada um tem a sua, <execucao>/<nome>, e todos rodam
    # em paralelo, até PARALELO juntos: cada ator e cada avaliador é um processo próprio, numa pasta própria.
    destinos = {nome: dest if len(lidos) == 1 else dest / nome for nome in lidos}
    with ThreadPoolExecutor(max_workers=min(len(lidos), PARALELO)) as grupo:
        futuros = {nome: grupo.submit(rodar_cenario, claude, fluxo, bot, nome, arquivo, pedido, sistema,
                                      destinos[nome], a.rodadas, a.modelo, dados, len(lidos) > 1)
                   for nome, (arquivo, _, pedido, sistema) in lidos.items()}
    incompletas = []
    for nome, futuro in futuros.items():
        # O erro de um cenário vira a linha de incompleta dele: os outros seguem até as tabelas.
        try:
            incompletas += futuro.result()
        except Exception as e:
            incompletas.append(f"cenario {nome or fluxo.name} parou com erro: {e!r}; veja {destinos[nome]}")
    for nome, pasta in destinos.items():
        if len(lidos) > 1:
            print(f"\n## {nome}\n")
        print(tabela([pasta]), end="")
    if incompletas:
        sys.exit("\n".join(incompletas))


if __name__ == "__main__":
    main()

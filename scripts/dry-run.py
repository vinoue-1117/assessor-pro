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

Roda pelo login do plano do Claude Code, sem chave de API.

Uso:
  python scripts/dry-run.py evals/analista/fluxo/tese [--saida PASTA]
  python scripts/dry-run.py evals/analista/gosto/layout --variantes [NOME ...] [--amostras M] [--partida PASTA] [--saida PASTA]
"""
import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
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


def ler_fluxo(fluxo, variante=None):
    """(pasta do bot, pedido, prompt de sistema) do ator, lidos antes de criar a pasta de execução.

    O `## Perfil` vem do `bot.md` da variante, se ela tiver um, e do bot se não tiver.
    """
    bot = pasta_do_bot(fluxo)
    ficha = variante / "bot.md" if variante and (variante / "bot.md").is_file() else bot / "bot.md"
    cenario = fluxo / "cenario.md"
    sistema = f"{secao(ficha, 'Perfil')}\n\n{secao(cenario, 'Plataforma')}"
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


def arquivar(dest, bot, fluxo, dados, sufixo="dry-run"):
    """Copia a pasta de execução para <dados>/execucoes/<bot>/<data>-<fluxo>-<sufixo> e devolve o destino.

    Segunda rodada no mesmo dia ganha o sufixo -2, a terceira -3.
    """
    base = dados / "execucoes" / bot.relative_to(ROOT / "bots") / f"{date.today().isoformat()}-{fluxo.name}-{sufixo}"
    alvo, n = base, 1
    while alvo.exists():
        n += 1
        alvo = base.with_name(f"{base.name}-{n}")
    shutil.copytree(dest, alvo)
    return alvo


def guardar(dest, bot, fluxo, dados, sufixo="dry-run"):
    """Copia a rodada para a pasta de dados, se houver uma, e devolve o destino (None sem cópia)."""
    if not dados:
        return None
    try:
        alvo = arquivar(dest, bot, fluxo, dados, sufixo)
    except OSError as e:
        # Falha da cópia não esconde o motivo da parada da rodada, que sai logo depois.
        print(f"copia falhou ({e}); a rodada continua em {dest}", file=sys.stderr, flush=True)
        return None
    print(f"copia: {alvo}", flush=True)
    return alvo


def atuar(claude, fluxo, pedido, sistema, dest):
    """Roda o ator na pasta de execução montada e devolve o exit dele.

    Grava sistema.md, transcript.jsonl e ator.err e, se o ator gravou algum evento, transcript.md.
    """
    arquivo_sistema = dest / "sistema.md"
    arquivo_sistema.write_text(sistema, encoding="utf-8", newline="\n")
    skills = sorted(d.name for d in (dest / ".claude" / "skills").iterdir())
    jsonl = dest / "transcript.jsonl"
    with open(jsonl, "w", encoding="utf-8") as saida, open(dest / "ator.err", "w", encoding="utf-8") as erros:
        # Sem subagente em segundo plano: na plataforma, o Task devolve a resposta do subagente na própria chamada.
        r = subprocess.run(comando_ator(claude, fluxo, arquivo_sistema, skills), cwd=dest, input=pedido,
                           env=ambiente(CLAUDE_CODE_DISABLE_BACKGROUND_TASKS="1"),
                           stdout=saida, stderr=erros, text=True, encoding="utf-8")
    linhas = jsonl.read_text(encoding="utf-8").splitlines()
    if linhas:
        (dest / "transcript.md").write_text(legivel(linhas), encoding="utf-8", newline="\n")
    return r.returncode


def indice(rodada, titulo, feitas):
    """Grava o index.html da rodada: uma linha por variante, uma coluna por amostra, com o link da page.html."""
    linhas = {}
    for variante, n, codigo, segundos in feitas:
        nome = html.escape(f"{variante}-{n}")
        celula = f'<a href="{nome}/page.html">{nome}</a>' if (rodada / f"{variante}-{n}" / "page.html").is_file() else f"{nome}: sem page.html"
        if codigo != 0:
            celula += f" (exit {codigo})"
        # Sem transcript.md o ator não emitiu nada, e o ator.err é o que explica a queda.
        log = "transcript.md" if (rodada / f"{variante}-{n}" / "transcript.md").is_file() else "ator.err"
        celula += f' <small>{segundos:.0f} s, <a href="{nome}/{log}">{log}</a></small>'
        linhas.setdefault(variante, []).append(f"<td>{celula}</td>")
    corpo = "\n".join(f"<tr><th>{html.escape(v)}</th>{''.join(c)}</tr>" for v, c in linhas.items())
    t = html.escape(titulo)
    (rodada / "index.html").write_text(
        f'<!doctype html>\n<meta charset="utf-8">\n<title>{t}</title>\n<h1>{t}</h1>\n<table>\n{corpo}\n</table>\n',
        encoding="utf-8", newline="\n",
    )


def gosto(claude, fluxo, bot, variantes, amostras, partida, rodada):
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
            codigo = atuar(claude, fluxo, ped, sis, dest)
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


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Dry run de um fluxo de bot com avaliacao do transcript, ou amostras de gosto.")
    p.add_argument("fluxo", help="pasta do cenario: evals/<bot>/fluxo/<fluxo>, ou evals/<bot>/gosto/<pergunta> com --variantes")
    p.add_argument("--saida", help="pasta nova, fora do repositorio (padrao: pasta temporaria)")
    p.add_argument("--variantes", nargs="*", metavar="NOME",
                   help="gosto: variantes de <cenario>/variantes/ (so a opcao: todas); sem avaliador")
    p.add_argument("--amostras", type=int, default=1, help="gosto: amostras de cada variante (padrao: 1)")
    p.add_argument("--partida", help="gosto: pasta copiada sobre cada pasta de execucao antes do ator (arquivos congelados)")
    a = p.parse_args()
    fluxo = Path(a.fluxo).resolve()
    if a.variantes is None:
        if (fluxo / "variantes").is_dir():
            sys.exit(f"{fluxo} tem variantes/: passe --variantes")
        if a.partida or a.amostras != 1:
            sys.exit("--amostras e --partida so valem com --variantes")
        bot, pedido, sistema = ler_fluxo(fluxo)
    else:
        bot = pasta_do_bot(fluxo)
        variantes = ler_variantes(fluxo, bot, a.variantes)
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
        prefixo = "dry-run" if a.variantes is None else "gosto"
        dest = Path(tempfile.mkdtemp(prefix=f"{prefixo}-{fluxo.name}-", dir=base))

    if a.variantes is not None:
        print(f"rodada: {dest}", flush=True)
        try:
            feitas = gosto(claude, fluxo, bot, variantes, a.amostras, partida, dest)
        finally:
            alvo = guardar(dest, bot, fluxo, dados, "gosto")
        print(f"indice: {(alvo or dest) / 'index.html'}")
        falhas = [f"{v}-{n}" for v, n, codigo, _ in feitas if codigo != 0 or not (dest / f"{v}-{n}" / "page.html").is_file()]
        if falhas:
            sys.exit(f"amostras com exit diferente de zero ou sem page.html: {', '.join(falhas)}")
        return

    pedido, sistema = montar(bot, pedido, sistema, dest)
    print(f"execucao: {dest}", flush=True)
    try:
        codigo = atuar(claude, fluxo, pedido, sistema, dest)
        if not (dest / "transcript.md").is_file():
            sys.exit(f"o ator nao gravou transcript (exit {codigo}); veja {dest / 'ator.err'}")
        print(f"ator: exit {codigo}, transcript em {dest / 'transcript.md'}", flush=True)
        # Ator que caiu no meio deixa um fluxo truncado: um relatório sobre ele mediria a queda, não a skill.
        if codigo != 0:
            sys.exit(f"rodada incompleta: o ator saiu com exit {codigo}, sem avaliacao; veja {dest / 'ator.err'}")
        (dest / "relatorio.md").write_text(avaliar(claude, fluxo, dest), encoding="utf-8", newline="\n")
        print(f"relatorio: {dest / 'relatorio.md'}")
    finally:
        # A rodada que parou no meio também é copiada: o transcript dela explica a parada.
        guardar(dest, bot, fluxo, dados)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Live run de um fluxo de bot: o avaliador lê o export de uma conversa do bot real, sem ator.

O export é a pasta que o bot do Grok Bot grava a pedido do dono, com a ferramenta ReadTranscript:
um `.jsonl` da sessão principal e um `.jsonl` por subagente, com `sand-subagent-<id>` no nome.
O script converte o trecho do fluxo para o `transcript.md` que o avaliador lê, grava a Page (o
`contents` do último `WriteCanvas` do trecho) em `page.md` e roda o agente `avaliador-transcript`
com a pasta do bot e o `anti-patterns.md` do fluxo. Não há cenário: o pedido é a mensagem do dono.

O trecho vai da mensagem do dono `--desde` (a marca `[tNu]` dela) até antes da mensagem `--ate`, ou
até o fim do export. Sem `--desde`, o script lista as mensagens do dono e para, a não ser que haja
uma só.

Formato que o conversor não conhece (papel, tipo de bloco, mensagem de usuário sem marca,
subagente sem arquivo) para o script com o arquivo e a linha do export. A skill `live-run` diz como
ajustar o conversor; o export nunca é editado à mão.

A pasta de execução fica fora do repositório e, com `ASSESSOR_EVALS_DADOS` no `.env`, é copiada
para `<pasta>/execucoes/<bot>/<data>-<fluxo>-live-run`, como no dry run.

Uso:
  python scripts/live-run.py evals/analista/fluxo/tese <pasta do export> [--desde tNu] [--ate tNu] [--saida PASTA]
"""
import argparse
import importlib.util
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("dry_run", ROOT / "scripts" / "dry-run.py")
dr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dr)

# Blocos que cada papel pode ter, com os campos obrigatórios de cada um.
BLOCOS = {
    "user": {"text": ("text",)},
    "assistant": {"text": ("text",), "thinking": ("thinking",), "tool_use": ("id", "name", "input")},
    "tool": {"tool_result": ("tool_use_id", "name", "result")},
}
# Mensagem do dono: a marca [tNu] logo depois da abertura do <user_query>.
DONO = re.compile(r"<user_query>\s*\[(t\d+u)\]")
PLATAFORMA = ("[GROK_BOT_HIDDEN_PROMPT]", "<memory_context>")
SUBAGENTE = re.compile(r"sand-subagent-[0-9a-f-]+")


class FormatoDesconhecido(Exception):
    """O export tem algo que o conversor não sabe ler. A mensagem traz o arquivo e a linha."""


def ler(arquivo):
    """Eventos do arquivo como (onde, papel, blocos), com `onde` = `<arquivo>:<linha>`. Para em formato desconhecido."""
    eventos = []
    for n, linha in enumerate(arquivo.read_text(encoding="utf-8").splitlines(), 1):
        if not linha.strip():
            continue
        onde = f"{arquivo.name}:{n}"
        try:
            evento = json.loads(linha)
            papel, blocos = evento["role"], evento["message"]["content"]
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            raise FormatoDesconhecido(f"{onde}: linha fora de {{role, message: {{content}}}} ({e})")
        if papel not in BLOCOS or not isinstance(blocos, list):
            raise FormatoDesconhecido(f"{onde}: papel {papel!r} ou content que nao e lista")
        for bloco in blocos:
            campos = BLOCOS[papel].get(bloco.get("type") if isinstance(bloco, dict) else None)
            if campos is None or any(c not in bloco for c in campos):
                raise FormatoDesconhecido(f"{onde}: bloco desconhecido para o papel {papel}: {str(bloco)[:200]}")
        eventos.append((onde, papel, blocos))
    return eventos


def ler_export(pasta):
    """(sessão principal, {id do subagente: arquivo}) da pasta do export."""
    principais, subagentes = [], {}
    for arquivo in sorted(pasta.glob("*.jsonl")):
        m = SUBAGENTE.search(arquivo.name)
        if m:
            subagentes[m[0]] = arquivo
        else:
            principais.append(arquivo)
    if len(principais) != 1:
        nomes = ", ".join(a.name for a in principais) or "nenhum"
        raise FormatoDesconhecido(f"{pasta}: esperado um .jsonl sem sand-subagent no nome (a sessao principal); achados: {nomes}")
    return principais[0], subagentes


def origem(texto, onde):
    """Rótulo de uma mensagem de usuário da sessão principal: do dono, com a marca, ou da plataforma."""
    m = DONO.search(texto)
    if m:
        return f"mensagem do dono [{m[1]}]"
    if any(marca in texto for marca in PLATAFORMA):
        return "mensagem da plataforma"
    raise FormatoDesconhecido(f"{onde}: mensagem de usuario sem a marca do dono ([tNu]) nem a da plataforma")


def mensagens_do_dono(eventos):
    """(marca, onde, primeira linha do texto) de cada mensagem do dono, na ordem."""
    achadas = []
    for onde, papel, blocos in eventos:
        for bloco in blocos:
            m = DONO.search(bloco.get("text", "")) if papel == "user" else None
            if m:
                linhas = [l for l in bloco["text"].split("<user_query>", 1)[1].splitlines()
                          if l.strip() and not l.startswith(("[", "<"))]
                achadas.append((m[1], onde, (linhas[0] if linhas else "")[:100]))
    return achadas


def entrada(bloco):
    """O input de um tool_use, que vem como objeto ou como JSON em texto. Texto que não é JSON volta como está."""
    valor = bloco["input"]
    if isinstance(valor, str):
        try:
            return json.loads(valor)
        except json.JSONDecodeError:
            return valor
    return valor


def trechos(eventos):
    """Os eventos de um subagente partidos em trechos, um por mensagem de entrada (a primeira chamada e cada retomada)."""
    partes = []
    for evento in eventos:
        if evento[1] == "user" or not partes:
            partes.append([])
        partes[-1].append(evento)
    return partes


def converter(principal, subagentes, desde, ate=None):
    """(transcript.md, Page ou None) do trecho da sessão principal entre as mensagens do dono `desde` e `ate`.

    Cada chamada de ferramenta ganha um número de passo, e o cabeçalho cita o arquivo e a linha do export.
    A chamada `CallDynamicTool` do `Task` liga ao arquivo do subagente pelo `sand-subagent-<id>` do
    resultado; o trecho do subagente entra logo depois desse resultado. O subagente retomado continua no
    mesmo arquivo: a enésima chamada com o mesmo id, contada desde o começo do export, recebe o enésimo
    trecho. Chamada e resultado repetidos com o mesmo id (o export repete eventos depois de um
    `<memory_context>`) entram uma vez.
    """
    saida = []
    chamadas = {}  # tool_use_id -> (passo, nome)
    tasks = set()  # tool_use_id das chamadas de Task
    respondidas = set()
    usados = {}  # id do subagente -> trechos já ligados
    partes = {}
    estado = {"passo": 0, "dentro": False, "page": None}

    def processar(eventos, quem, principal_):
        for onde, papel, blocos in eventos:
            if principal_ and papel == "user":
                for bloco in blocos:
                    m = DONO.search(bloco["text"])
                    if m and m[1] == desde:
                        estado["dentro"] = True
                    elif m and m[1] == ate:
                        estado["dentro"] = False
            dentro = estado["dentro"]
            for bloco in blocos:
                tipo = bloco["type"]
                if tipo == "tool_use":
                    if bloco["id"] in chamadas:
                        continue
                    valor = entrada(bloco)
                    nome = bloco["name"]
                    if isinstance(valor, dict) and nome == "CallDynamicTool":
                        args = valor.get("arguments") or {}
                        if valor.get("toolName") == "Task":
                            tasks.add(bloco["id"])
                            nome = f"Task {args.get('subagent_type', '?')}" + (", retomada" if args.get("resume") else "")
                        else:
                            nome = valor.get("toolName") or nome
                    elif isinstance(valor, dict) and nome == "Skill":
                        nome = f"Skill {valor.get('name', '?')}"
                    if dentro:
                        estado["passo"] += 1
                        if bloco["name"] == "WriteCanvas":
                            estado["page"] = valor.get("contents", "") if isinstance(valor, dict) else valor
                        corpo = valor["command"] if isinstance(valor, dict) and "command" in valor else (
                            valor if isinstance(valor, str) else json.dumps(valor, ensure_ascii=False, indent=1))
                        saida.append(f"## passo {estado['passo']}: {quem} chama {bloco['name']} ({nome}) [{onde}]\n\n```\n{corpo}\n```")
                    chamadas[bloco["id"]] = (estado["passo"] if dentro else "fora do trecho", nome)
                elif tipo == "tool_result":
                    ident = bloco["tool_use_id"]
                    if ident in respondidas:
                        continue
                    respondidas.add(ident)
                    passo, nome = chamadas.get(ident, ("?", bloco["name"]))
                    if dentro:
                        saida.append(f"### resultado do passo {passo} ({nome}), para {quem} [{onde}]\n\n```\n{bloco['result']}\n```")
                    m = SUBAGENTE.search(bloco["result"]) if ident in tasks else None
                    if m:
                        sub = m[0]
                        if sub not in subagentes:
                            raise FormatoDesconhecido(f"{onde}: {sub} sem arquivo na pasta do export")
                        if sub not in partes:
                            partes[sub] = trechos(ler(subagentes[sub]))
                        k = usados.get(sub, 0)
                        if k >= len(partes[sub]):
                            raise FormatoDesconhecido(f"{onde}: chamada {k + 1} de {sub}, que so tem {len(partes[sub])} mensagens de entrada")
                        usados[sub] = k + 1
                        if dentro:
                            processar(partes[sub][k], f"subagente {nome.removeprefix('Task ').split(',')[0]} do passo {passo}", False)
                elif dentro and tipo == "text" and papel == "user":
                    rotulo = origem(bloco["text"], onde) if principal_ else f"entrada para {quem}"
                    saida.append(f"### {rotulo} [{onde}]\n\n{bloco['text']}")
                elif dentro and tipo in ("text", "thinking") and bloco[tipo].strip():
                    saida.append(f"### {'texto' if tipo == 'text' else 'raciocinio'} de {quem} [{onde}]\n\n{bloco[tipo]}")

    processar(ler(principal), "bot", True)
    if ate is None:
        sobra = [f"{sub} ({len(p) - usados.get(sub, 0)})" for sub, p in partes.items() if usados.get(sub, 0) < len(p)]
        if sobra:
            raise FormatoDesconhecido(f"mensagens de entrada de subagente sem chamada de Task: {', '.join(sobra)}")
    fim = f"ate antes da mensagem do dono [{ate}]" if ate else "ate o fim do export"
    cabeca = (
        "# Transcript do bot\n\n"
        f"origem: export {principal.name}, da mensagem do dono [{desde}] {fim}\n\n"
        "entrega ao dono: a chamada SendToUser; o texto solto do bot nao chega ao dono\n\n"
        "Page: o contents da ultima chamada WriteCanvas, gravado em page.md; edicao posterior da Page (EditCanvas) so aparece nos passos\n\n"
        "teto do export: todo bloco com mais de uns 4.000 caracteres vem com o meio trocado por '...', sem outro aviso"
    )
    return "\n\n".join([cabeca, *saida]) + "\n", estado["page"]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    # A lista de mensagens do dono sai pelo sys.exit, no stderr, com o acento do texto dele.
    sys.stderr.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Live run: o avaliador le o export de uma conversa do bot real, sem ator.")
    p.add_argument("fluxo", help="pasta do fluxo: evals/<bot>/fluxo/<fluxo>")
    p.add_argument("export", help="pasta do export: a sessao principal e os arquivos sand-subagent-<id>")
    p.add_argument("--desde", help="marca [tNu] da mensagem do dono que comeca o fluxo (sem ela, lista as mensagens)")
    p.add_argument("--ate", help="marca [tNu] da mensagem do dono que fica fora, e tudo depois dela")
    p.add_argument("--saida", help="pasta nova, fora do repositorio (padrao: pasta temporaria)")
    a = p.parse_args()
    fluxo = Path(a.fluxo).resolve()
    bot = dr.pasta_do_bot(fluxo)
    if not (fluxo / "anti-patterns.md").is_file():
        sys.exit(f"{fluxo} sem anti-patterns.md")
    export = Path(a.export).resolve()
    if not export.is_dir():
        sys.exit(f"{export} nao e uma pasta")
    try:
        principal, subagentes = ler_export(export)
        marcas = mensagens_do_dono(ler(principal))
    except FormatoDesconhecido as e:
        sys.exit(f"formato desconhecido: {e}")
    lista = "\n".join(f"  {m} ({onde}): {texto}" for m, onde, texto in marcas) or "  nenhuma"
    desde = a.desde or (marcas[0][0] if len(marcas) == 1 else None)
    if desde is None:
        sys.exit(f"passe --desde com a mensagem do dono que comeca o fluxo e, se o fluxo acaba antes do fim, --ate:\n{lista}")
    validas = [m for m, _, _ in marcas]
    for marca in (desde, a.ate):
        if marca and marca not in validas:
            sys.exit(f"{marca} nao e mensagem do dono neste export:\n{lista}")
    if a.ate and validas.index(a.ate) <= validas.index(desde):
        sys.exit(f"--ate {a.ate} tem que vir depois de --desde {desde}")
    try:
        transcript, page = converter(principal, subagentes, desde, a.ate)
    except FormatoDesconhecido as e:
        sys.exit(f"formato desconhecido: {e}")

    claude = shutil.which("claude")
    if not claude:
        sys.exit("claude fora do PATH")
    base = Path(a.saida).resolve() if a.saida else Path(tempfile.gettempdir()).resolve()
    # O repositório é público: transcript e relatório nunca ficam dentro dele.
    if base == ROOT or ROOT in base.parents:
        sys.exit(f"{base} fica dentro do repositorio: use uma pasta de fora")
    dados = dr.pasta_de_dados()
    if dados and (not dados.is_dir() or dados == ROOT or ROOT in dados.parents):
        sys.exit(f"{dr.VAR_DADOS} do .env ({dados}) tem que ser uma pasta que existe, fora do repositorio")
    if a.saida:
        if base.exists():
            sys.exit(f"{base} ja existe: passe em --saida uma pasta nova")
        base.mkdir(parents=True)
        dest = base
    else:
        dest = Path(tempfile.mkdtemp(prefix=f"live-run-{fluxo.name}-", dir=base))

    try:
        (dest / "transcript.md").write_text(transcript, encoding="utf-8", newline="\n")
        if page is not None:
            (dest / "page.md").write_text(page, encoding="utf-8", newline="\n")
        print(f"transcript: {dest / 'transcript.md'}", flush=True)
        try:
            relatorio = dr.avaliar(claude, fluxo, dest, live=True)
        except RuntimeError as e:
            sys.exit(f"{e}; transcript em {dest}")
        (dest / "relatorio.md").write_text(relatorio, encoding="utf-8", newline="\n")
        print(f"relatorio: {dest / 'relatorio.md'}", flush=True)
    finally:
        dr.guardar(dest, bot, fluxo, dados, "live-run")


if __name__ == "__main__":
    main()

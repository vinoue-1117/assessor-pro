#!/usr/bin/env python3
"""Gera ponteiros, copia os plugins e atualiza os comandos de download.

A fonte dos bots fica em bots/<produto>/. plugins/ é cópia gerada: o
marketplace instala dali e os bots já em produção baixam essas URLs da
branch stable. template/<produto>/skills/ são os ponteiros.

A description de cada ponteiro fica no mapa DESCRICOES: uma frase fixa
sobre quando usar a skill. Ela não é copiada da skill completa.

Uso:
  python3 tools/gerar-ponteiros.py
  python3 tools/gerar-ponteiros.py --check
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from comum.baixar import (  # noqa: E402
    CLIENTE_ANTIGO,
    CLIENTE_NOVO,
    DISCURSO,
    MIN_ANTIGO,
    MIN_NOVO,
    SCRIPT_ANTIGO,
    SCRIPT_NOVO,
    SKILLS_ASSESSOR,
    SKILLS_CLIENTE,
    SKILLS_DISCURSO,
    comando_assessor,
    comando_cliente,
    comando_discurso,
    comando_ponteiro,
)

PLUGINS_FONTE = {
    "assessor-envio": ROOT / "bots/assessor/envio",
    "assessor-zap": ROOT / "bots/assessor/zap",
}
PLUGINS = ROOT / "plugins"
OUT = ROOT / "template" / "assessor" / "skills"
FALHA = (
    "Não consegui baixar as instruções atuais do Assessor Pro. "
    "Tente de novo em alguns minutos."
)

# Quando usar cada skill. Texto estável, mantido só aqui: não acompanhe
# a description da skill completa (ela muda com implementação, arquivo,
# versão e regra de trava). Comece pelas palavras-gatilho já em uso.
DESCRICOES = {
    "assessor-ajustar-cliente": "Use quando o assessor pedir por mensagem para adicionar, alterar ou remover um cliente da planilha salva (conta, telefone, nome ou apelido), sem mandar a planilha inteira.",
    "assessor-enviar-relatorio": "Use só depois que o assessor aprovou no chat o resumo do lote gerado por assessor-preparar-envio, para enviar os relatórios aos clientes pelo bot de WhatsApp.",
    "assessor-envio-core": "Persona e regras do bot Relatórios - Assessor Pro: siga em toda conversa deste bot.",
    "assessor-envio-teste": "Use quando o assessor quiser ver como um relatório chega no WhatsApp antes do envio real, sem enviar a nenhum cliente.",
    "assessor-preparar-envio": "Use quando o assessor mandar no chat o zip do lote do relatório mensal de performance da corretora e/ou a planilha de clientes, ou pedir para preparar o envio mensal dos relatórios por WhatsApp.",
    "assessor-rastrear-apelido": "Use quando o assessor pedir para preencher ou corrigir a coluna apelido da planilha de clientes a partir de como ele chama cada cliente no WhatsApp.",
    "assessor-resumo-ultimo-envio": "Use quando o assessor perguntar como foi o último envio de relatórios (quantos foram, quais falharam e por quê).",
    "assessor-zap-core": "Persona e regras do bot Whatsapp - Assessor Pro: siga em toda conversa deste bot.",
    "assessor-zap-enviar": "Use quando outro bot pedir para enviar no WhatsApp um texto e/ou um arquivo para um contato.",
    "assessor-zap-exportar-historico": "Use quando outro bot ou o dono pedir para ler ou exportar mensagens de uma ou mais conversas do WhatsApp.",
    "assessor-zap-triagem": "Use na rotina de leitura do WhatsApp para ler as conversas que têm rota e encaminhar cada mensagem nova ao bot dono da rota.",
}

PLUGIN_DO_BOT = {"envio": "assessor-envio", "zap": "assessor-zap"}


def linha_description(nome):
    if nome not in DESCRICOES:
        sys.exit(f"sem description de ponteiro: {nome}")
    texto = DESCRICOES[nome]
    if not texto.strip() or "\n" in texto:
        sys.exit(f"description de ponteiro inválida: {nome}")
    return "description: '" + texto.replace("'", "''") + "'"


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


def skills_fonte():
    achados = []
    for fonte in PLUGINS_FONTE.values():
        achados.extend(sorted(fonte.glob("skills/*/SKILL.md")))
    return achados


def rels_da_skill(path):
    rel = path.relative_to(ROOT).as_posix()
    partes = rel.split("/")
    # bots/assessor/<envio|zap>/skills/<nome>/SKILL.md
    if len(partes) != 6 or partes[0] != "bots" or partes[3] != "skills":
        sys.exit(f"skill fora do layout: {rel}")
    plugin = PLUGIN_DO_BOT.get(partes[2])
    if not plugin:
        sys.exit(f"bot sem plugin: {rel}")
    antigo = f"plugins/{plugin}/skills/{partes[4]}/SKILL.md"
    return rel, antigo


def comandos_da_skill(nome):
    cmds = []
    if nome in SKILLS_ASSESSOR:
        cmds.append(comando_assessor())
    if nome in SKILLS_CLIENTE:
        cmds.append(comando_cliente())
    if nome in SKILLS_DISCURSO:
        cmds.append(comando_discurso())
    return cmds


def spans(texto):
    achados = []
    i = 0
    while i < len(texto):
        a = texto.find("`", i)
        if a < 0:
            break
        b = texto.find("`", a + 1)
        if b < 0:
            break
        if "\n" in texto[a:b]:
            i = a + 1
            continue
        achados.append((a, b, texto[a + 1:b]))
        i = b + 1
    return achados


def qual_comando(content):
    if "raw.githubusercontent.com" not in content and "python3 -c " not in content:
        return None
    if "/workspace/assessor/cliente.py" in content or "/scripts/cliente.py" in content:
        return comando_cliente()
    if "discurso-macro.md" in content or "/workspace/assessor/discurso.md" in content:
        return comando_discurso()
    if (
        "/workspace/assessor/assessor.py" in content
        or "/scripts/assessor.py" in content
        or "$b/assessor.py" in content
    ):
        return comando_assessor()
    return None


def reescrever(texto):
    for start, end, content in reversed(spans(texto)):
        cmd = qual_comando(content)
        if cmd is None or cmd == content:
            continue
        texto = texto[:start] + "`" + cmd + "`" + texto[end + 1:]
    return texto


def atualizar_skills():
    for path in skills_fonte():
        texto = reescrever(path.read_text(encoding="utf-8"))
        nome = path.parent.name
        if "curl -fsSL https://raw.githubusercontent.com" in texto:
            sys.exit(f"curl antigo ainda na skill: {path.relative_to(ROOT)}")
        for cmd in comandos_da_skill(nome):
            if cmd not in texto:
                sys.exit(f"não achei onde gravar o comando em {path.relative_to(ROOT)}")
            if "`" in cmd:
                sys.exit(f"comando com crase: {nome}")
        path.write_text(texto, encoding="utf-8")


def carregar():
    ponteiros = {}
    for path in skills_fonte():
        texto = path.read_text(encoding="utf-8")
        nome_linha, _ = frontmatter(texto, path)
        nome = nome_linha.split(":", 1)[1].strip().strip("'\"")
        if not nome:
            sys.exit(f"name vazio: {path}")
        if nome in ponteiros:
            sys.exit(f"nome de skill repetido: {nome}")
        rel_novo, rel_antigo = rels_da_skill(path)
        ponteiros[nome] = ponteiro(nome, nome_linha, rel_novo, rel_antigo)
    if not ponteiros:
        sys.exit(f"nenhuma skill em {PLUGINS_FONTE}")
    extras = sorted(set(DESCRICOES) - set(ponteiros))
    if extras:
        sys.exit("description de ponteiro sem skill: " + ", ".join(extras))
    return ponteiros


def ponteiro(nome, nome_linha, rel_novo, rel_antigo):
    url_cmd = comando_ponteiro(f"/workspace/assessor-pro/{nome}.md", rel_novo, rel_antigo)
    desc_linha = linha_description(nome)
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
        f"1. `{url_cmd}`\n"
        f"2. Confira que `{destino}` começa com frontmatter (`---`) e tem `{nome_linha}`.\n"
        "3. Siga exatamente o que foi baixado.\n"
        "\n"
        "Se o comando disser para definir GITHUB_TOKEN_BOTS, pare e repasse essa mensagem ao assessor. "
        "Não use cópia antiga nem improvise.\n"
        "\n"
        f'Se o download falhar por outro motivo, vier vazio ou a conferência não bater, pare e diga ao assessor: "{FALHA}" '
        "Não use cópia antiga nem improvise.\n"
    )


def refs_main():
    ruins = []
    pastas = [(fonte, "skills/*/SKILL.md") for fonte in PLUGINS_FONTE.values()]
    pastas.append((OUT, "*/SKILL.md"))
    pastas.append((PLUGINS, "*/skills/*/SKILL.md"))
    for pasta, glob in pastas:
        if not pasta.exists():
            continue
        for path in sorted(pasta.glob(glob)):
            if "/main/" in path.read_text(encoding="utf-8"):
                ruins.append(path.relative_to(ROOT).as_posix())
    return ruins


def arquivos(raiz):
    return {
        p.relative_to(raiz).as_posix(): p.read_bytes()
        for p in raiz.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and not p.name.endswith(".pyc")
    }


def sincronizar_plugins():
    if PLUGINS.exists():
        for filho in PLUGINS.iterdir():
            if filho.is_dir():
                shutil.rmtree(filho)
            else:
                filho.unlink()
    else:
        PLUGINS.mkdir(parents=True)
    for nome, fonte in PLUGINS_FONTE.items():
        shutil.copytree(
            fonte,
            PLUGINS / nome,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )


def caminhos_obrigatorios():
    lista = [
        SCRIPT_NOVO,
        SCRIPT_ANTIGO,
        MIN_NOVO,
        MIN_ANTIGO,
        CLIENTE_NOVO,
        CLIENTE_ANTIGO,
        DISCURSO,
    ]
    for path in skills_fonte():
        novo, antigo = rels_da_skill(path)
        lista.extend((novo, antigo))
    return lista


def pares_iguais():
    return (
        (SCRIPT_NOVO, SCRIPT_ANTIGO),
        (MIN_NOVO, MIN_ANTIGO),
        (CLIENTE_NOVO, CLIENTE_ANTIGO),
    )


def conferir_comandos():
    problemas = []
    for path in skills_fonte():
        texto = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        if "curl -fsSL https://raw.githubusercontent.com" in texto:
            problemas.append(f"curl antigo: {rel}")
        for cmd in comandos_da_skill(path.parent.name):
            if cmd not in texto:
                problemas.append(f"comando de download desatualizado: {rel}")
        copia = PLUGINS / "assessor-envio" / path.relative_to(PLUGINS_FONTE["assessor-envio"]) if path.is_relative_to(PLUGINS_FONTE["assessor-envio"]) else PLUGINS / "assessor-zap" / path.relative_to(PLUGINS_FONTE["assessor-zap"])
        if copia.is_file() and copia.read_text(encoding="utf-8") != texto:
            problemas.append(f"plugin diferente da fonte: {copia.relative_to(ROOT)}")
    return problemas


def conferir_plugins():
    problemas = []
    for nome, fonte in PLUGINS_FONTE.items():
        dest = PLUGINS / nome
        if not dest.is_dir():
            problemas.append(f"falta o plugin gerado {dest.relative_to(ROOT)}")
            continue
        if arquivos(fonte) != arquivos(dest):
            problemas.append(f"plugin desatualizado: plugins/{nome}")
    return problemas


def conferir_caminhos():
    problemas = []
    for rel in caminhos_obrigatorios():
        if not (ROOT / rel).is_file():
            problemas.append(f"caminho publicado ausente: {rel}")
    for novo, antigo in pares_iguais():
        a = ROOT / novo
        b = ROOT / antigo
        if a.is_file() and b.is_file() and a.read_bytes() != b.read_bytes():
            problemas.append(f"cópia antiga diferente da fonte: {antigo}")
    return problemas


def gravar(esperado):
    atualizar_skills()
    sincronizar_plugins()
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
    # as skills mudaram; recarrega os ponteiros depois dos comandos novos
    esperado = carregar()
    for nome in sorted(esperado):
        dest = OUT / nome / "SKILL.md"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(esperado[nome], encoding="utf-8")
    print(f"ponteiros gravados: {len(esperado)}")
    return esperado


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
    problemas.extend(conferir_plugins())
    problemas.extend(conferir_comandos())
    problemas.extend(conferir_caminhos())
    if problemas:
        print("ponteiros desatualizados:", file=sys.stderr)
        for item in problemas:
            print(f"- {item}", file=sys.stderr)
        print("rode: python3 tools/gerar-ponteiros.py", file=sys.stderr)
        sys.exit(1)
    print(f"ponteiros ok ({len(esperado)})")


def main():
    if "--check" in sys.argv:
        conferir(carregar())
    else:
        conferir(gravar(carregar()))


if __name__ == "__main__":
    main()

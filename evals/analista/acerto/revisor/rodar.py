#!/usr/bin/env python3
"""Eval do revisor da tese: os papeis de revisor sobre rascunhos de tese e o pacote de dados.

Monta os casos de CASOS numa pasta fora do repositorio, grava o relatorio de
entrada (entrada.html), roda o `claude plugin eval` pelo login do plano e soma
a regua a partir do JSON de resultado. O papel de cada caso vem dos arquivos
`papel-*.md` desta pasta.

Uso:
  python evals/analista/acerto/revisor/rodar.py [--runs N] [--caso GLOB] [--saida PASTA] [--so-entrada]
"""
import argparse
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
MODELO = "sonnet"
# A palavra "veredito" ou "resultado" seguida do termo, so com pontuacao ou marca no meio.
# "o resultado confere com o JSON", no corpo da resposta, nao casa.
VEREDITO = re.compile(
    r"(?:veredito|resultado)(?: final)?[ \t*`_]*[:\n—–-][\s*`_]*(s[oó]lida|fr[aá]gil|refazer|confere|reescrever)\b", re.I
)
# Nome do caso: (papel, rascunho, gabarito).
CASOS = {
    "advogado": ("papel-advogado.md", "rascunho.md", "gabarito.json"),
    "advogado-limpo": ("papel-advogado.md", "rascunho-limpo.md", "gabarito-limpo.json"),
    "conferente": ("papel-conferente.md", "rascunho.md", "gabarito.json"),
    "conferente-limpo": ("papel-conferente.md", "rascunho-limpo.md", "gabarito-limpo.json"),
    "conferente-itens": ("papel-conferente.md", "rascunho-itens.md", "gabarito-itens.json"),
    "conferente-limitacao": ("papel-conferente.md", "rascunho-limitacao.md", "gabarito-limitacao.json"),
    "antagonista": ("papel-antagonista.md", "rascunho.md", "gabarito-antagonista.json"),
    "antagonista-limpo": ("papel-antagonista.md", "rascunho-limpo.md", "gabarito-antagonista.json"),
}
TITULO = {
    "rascunho.md": "Rascunho com erros plantados",
    "rascunho-limpo.md": "Rascunho sem erro",
    "rascunho-itens.md": "Rascunho sem erro, com os itens do antagonista",
    "rascunho-limitacao.md": "Rascunho sem erro, com a frase de limitação",
}
ROTULO = {"erro": "erro plantado", "correta": "frase correta", "aprova": "veredito", "hipotese": "hipótese", "papel": "papel"}
CSS = """
:root{--fundo:#f6f5f1;--cartao:#fff;--texto:#1c1b19;--suave:#5f5c55;--borda:#d6d2c8;--erro:#f6c9c0;--correta:#c9e8cf;--aprova:#cfd8f0;--hipotese:#f3e2b0}
@media (prefers-color-scheme:dark){:root{--fundo:#17171a;--cartao:#212126;--texto:#ecebe7;--suave:#a8a59d;--borda:#3a3a42;--erro:#7a2e22;--correta:#225a31;--aprova:#2c3a63;--hipotese:#6b5516}}
body{margin:0;padding:32px 16px 48px;background:var(--fundo);color:var(--texto);font:17px/1.55 system-ui,"Segoe UI",sans-serif}
main{max-width:900px;margin:0 auto}
section{background:var(--cartao);border:1px solid var(--borda);border-radius:10px;padding:8px 22px 16px;margin:0 0 20px}
h1{font-size:1.6rem;margin:0 0 4px} h2{font-size:1.2rem} h3{font-size:1.05rem}
.suave{color:var(--suave)}
mark{color:inherit;padding:1px 3px;border-radius:4px} mark.erro{background:var(--erro)} mark.correta{background:var(--correta)} mark.aprova,mark.papel{background:var(--aprova)} mark.hipotese{background:var(--hipotese)}
pre{overflow-x:auto;font:.85rem/1.45 ui-monospace,Consolas,monospace}
code{font:.9em ui-monospace,Consolas,monospace}
table{border-collapse:collapse;width:100%} td,th{border-top:1px solid var(--borda);padding:8px 10px 8px 0;text-align:left;vertical-align:top}
"""


def ler(nome):
    return (AQUI / nome).read_text(encoding="utf-8").strip()


def esc(texto):
    return html.escape(texto, quote=False)


def por_rascunho():
    """Rascunho -> gabarito -> casos que usam os dois."""
    saida = {}
    for nome, (_, rascunho, gab) in CASOS.items():
        saida.setdefault(rascunho, {}).setdefault(gab, []).append(nome)
    return saida


def gabarito(arquivo):
    """Nome do criterio e o trecho do rascunho que ele confere (vazio: a resposta inteira)."""
    return json.loads(ler(arquivo))


def montar(dest, runs):
    """Grava em dest/evals um caso por entrada de CASOS: o papel, o rascunho e o JSON, com os criterios do gabarito."""
    for nome, (papel, rascunho, gab) in CASOS.items():
        caso = Path(dest) / "evals" / nome
        (caso / "graders").mkdir(parents=True)
        for criterio in gabarito(gab):
            shutil.copy(AQUI / "graders" / f"{criterio}.md", caso / "graders")
        texto = (
            f"---\nruns: {runs}\nmax_turns: 3\nallowed_tools: []\n---\n\nPapel: {ler(papel)}\n\n"
            f"## Rascunho\n\n{ler(rascunho)}\n\n## JSON\n\n```json\n{ler('dados.json')}\n```\n"
        )
        (caso / "prompt.md").write_text(texto, encoding="utf-8", newline="\n")


def rascunho_marcado(rascunho, gabs):
    """HTML do rascunho com cada trecho dos gabaritos marcado. O revisor recebe o texto sem marca."""
    texto = esc(ler(rascunho))
    for gab in gabs:
        for nome, trecho in gabarito(gab).items():
            if trecho:
                texto = texto.replace(esc(trecho), f'<mark class="{nome.split("-")[0]}" title="{nome}">{esc(trecho)}</mark>')
    texto = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", texto)
    blocos = []
    for bloco in texto.split("\n\n"):
        if bloco.startswith("#"):
            blocos.append(f"<h3>{bloco.lstrip('# ')}</h3>")
        elif bloco.startswith("- "):
            blocos.append("<ul>" + "".join(f"<li>{l[2:]}</li>" for l in bloco.split("\n")) + "</ul>")
        else:
            blocos.append(f"<p>{bloco}</p>")
    return "\n".join(blocos)


def tabela_criterios(gab):
    linhas = ""
    for nome, trecho in gabarito(gab).items():
        passa = next(l for l in ler(f"graders/{nome}.md").splitlines() if l.startswith("PASS: "))
        tipo = nome.split("-")[0]
        linhas += (
            f'<tr><td><code>{nome}</code></td><td><mark class="{tipo}">{ROTULO[tipo]}</mark></td>'
            f"<td>{esc(trecho) or '(a resposta inteira)'}</td><td>{esc(passa[6:])}</td></tr>"
        )
    return f"<table><tr><th>Critério</th><th>Tipo</th><th>Trecho do rascunho</th><th>Passa quando</th></tr>{linhas}</table>"


def relatorio_entrada(dest, runs):
    """Grava dest/entrada.html: os papeis, cada rascunho com os gabaritos e os criterios, e o JSON."""
    por_papel = {}
    for nome, (papel, *_) in CASOS.items():
        por_papel.setdefault(ler(papel), []).append(nome)
    papeis = "".join(f"<h3>{', '.join(casos)}</h3><p>{esc(texto)}</p>" for texto, casos in por_papel.items())
    rascunhos = "".join(
        f"<section><h2>{TITULO[rascunho]}</h2>{rascunho_marcado(rascunho, gabs)}"
        + "".join(f"<h3>Critérios do juiz: {', '.join(casos)}</h3>{tabela_criterios(gab)}" for gab, casos in gabs.items())
        + "</section>"
        for rascunho, gabs in por_rascunho().items()
    )
    pagina = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Entrada do eval do revisor</title><style>{CSS}</style></head><body><main>
<h1>Entrada do eval do revisor</h1>
<p class="suave">{runs} execuções por caso. Revisor e juiz em {MODELO}. Cada caso recebe o papel, um rascunho e o JSON, sem as marcas.
O juiz recebe a resposta do revisor e um critério por vez, e vota três vezes.</p>
<p class="suave"><mark class="erro">erro plantado</mark> <mark class="correta">frase correta</mark> <mark class="hipotese">hipótese</mark> O nome do critério aparece ao passar o mouse.</p>
<section><h2>Papéis</h2>{papeis}</section>
{rascunhos}
<section><h2>JSON</h2><pre>{esc(ler('dados.json'))}</pre></section>
</main></body></html>
"""
    caminho = Path(dest) / "entrada.html"
    caminho.write_text(pagina, encoding="utf-8", newline="\n")
    return caminho


def veredito(resposta):
    """O ultimo veredito ou resultado que a resposta declara, ou None."""
    achados = VEREDITO.findall(resposta)
    return achados[-1].lower() if achados else None


def descarte(execucao):
    """Motivo para a execucao ficar fora da soma, ou None.

    Resposta vazia ou cortada fica fora: os criterios `correta-*` e `papel-*`
    passam quando a resposta nao traz nada. Do papel que da veredito, a prova e
    o veredito; do que nao da (criterio `papel-sem-veredito`), um item de lista.
    """
    if execucao.get("error"):
        return f"erro: {execucao['error']}"
    graders = execucao.get("graders") or []
    if not graders:
        return "nenhum criterio julgado"
    sem = [g["name"] for g in graders if not isinstance(g.get("passed"), bool)]
    if sem:
        return f"criterio sem julgamento: {', '.join(sem)}"
    # O `evidence` de todo criterio e a resposta inteira do revisor.
    resposta = graders[0].get("evidence") or ""
    if any(g["name"] == "papel-sem-veredito" for g in graders):
        if not re.search(r"^\s*[-*] \S", resposta, re.M):
            return f"resposta sem nenhum item: {resposta[:200]!r}"
    elif not veredito(resposta):
        return f"resposta sem veredito: {resposta[:200]!r}"
    return None


def somar(resultado):
    """Por caso, uma linha por execucao: erros pegos, corretas contestadas, hipoteses apontadas, criterios do papel cumpridos, aprovou (None sem o criterio), o veredito e a resposta."""
    saida = {}
    for caso in resultado["cases"]:
        linhas = []
        for execucao in caso["arms"]["with"]:
            motivo = descarte(execucao)
            if motivo:
                print(f"execucao de {caso['name']} fora da soma: {motivo}", file=sys.stderr)
                continue
            linha = {"erros": 0, "de_erros": 0, "contestadas": 0, "de_corretas": 0,
                     "apontadas": 0, "de_hipoteses": 0, "papel": 0, "de_papel": 0, "aprovou": None}
            for g in execucao["graders"]:
                if g["name"].startswith("erro-"):
                    linha["erros"] += g["passed"]
                    linha["de_erros"] += 1
                elif g["name"].startswith("correta-"):
                    linha["contestadas"] += not g["passed"]
                    linha["de_corretas"] += 1
                elif g["name"].startswith("hipotese-"):
                    linha["apontadas"] += g["passed"]
                    linha["de_hipoteses"] += 1
                elif g["name"].startswith("papel-"):
                    linha["papel"] += g["passed"]
                    linha["de_papel"] += 1
                elif g["name"] == "aprova":
                    linha["aprovou"] = g["passed"]
                else:
                    sys.exit(f"criterio fora da regua: {g['name']}")
            linha["resposta"] = execucao["graders"][0]["evidence"]
            linha["veredito"] = veredito(linha["resposta"])
            linhas.append(linha)
        saida[caso["name"]] = linhas
    return saida


def resumo(valores):
    return f"{sum(valores) / len(valores):.1f} ({min(valores)} a {max(valores)})"


def relatar(soma, dest):
    respostas = Path(dest) / "respostas"
    respostas.mkdir(exist_ok=True)
    for caso, linhas in soma.items():
        print(f"\n{caso} ({len(linhas)} execucoes)")
        if not linhas:
            continue
        if linhas[0]["de_erros"]:
            print(f"  erros plantados pegos (de {linhas[0]['de_erros']}): {resumo([l['erros'] for l in linhas])}")
        if linhas[0]["de_corretas"]:
            print(f"  frases corretas contestadas (de {linhas[0]['de_corretas']}): {resumo([l['contestadas'] for l in linhas])}")
        if linhas[0]["de_hipoteses"]:
            print(f"  itens de hipotese apontados (de {linhas[0]['de_hipoteses']}): {resumo([l['apontadas'] for l in linhas])}")
        if linhas[0]["de_papel"]:
            print(f"  criterios do papel cumpridos (de {linhas[0]['de_papel']}): {resumo([l['papel'] for l in linhas])}")
        if linhas[0]["aprovou"] is not None:
            print(f"  execucoes em que o revisor aprovou a tese: {sum(l['aprovou'] for l in linhas)} de {len(linhas)}")
        for i, linha in enumerate(linhas, 1):
            (respostas / f"{caso}-{i}.md").write_text(linha["resposta"], encoding="utf-8", newline="\n")
            print(f"  veredito {i}: {linha['veredito'] or 'sem veredito'}")
    print(f"\nafirmacoes de fora do rascunho e do JSON: contar a mao nas respostas em {respostas}")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Eval do revisor da tese pelo claude plugin eval.")
    p.add_argument("--runs", type=int, default=5, help="execucoes por caso (padrao: 5)")
    p.add_argument("--caso", help="glob do nome do caso, por exemplo *-limpo (padrao: todos)")
    p.add_argument("--saida", help="pasta nova, fora do repositorio (padrao: pasta temporaria)")
    p.add_argument("--so-entrada", action="store_true", help="monta os casos e o entrada.html, sem rodar o eval")
    a = p.parse_args()
    dest = Path(a.saida).resolve() if a.saida else Path(tempfile.mkdtemp(prefix="eval-revisor-"))
    if (dest / "evals").exists():
        sys.exit(f"{dest} ja tem casos montados: passe em --saida uma pasta nova")
    montar(dest, a.runs)
    print(f"entrada: {relatorio_entrada(dest, a.runs)}")
    if a.so_entrada:
        return
    claude = shutil.which("claude")
    if not claude:
        sys.exit("claude fora do PATH")
    json_path = dest / "aggregate-result.json"
    relatorio = dest / "relatorio.html"
    # Sem --no-publish o relatorio e publicado no claude.ai. O exit code 1 so diz
    # que algum caso ficou abaixo da nota 1.0, o que aqui e esperado.
    comando = [claude, "plugin", "eval", ".", "--no-publish", "--trust-plugin", "--model", MODELO,
               "--judge-model", MODELO, "-j", "2", "--output-dir", str(dest), "--report", str(relatorio)]
    if a.caso:
        comando += ["--case", a.caso]
    subprocess.run(comando, cwd=dest)
    if not json_path.is_file():
        sys.exit(f"o claude plugin eval nao gravou {json_path}")
    relatar(somar(json.loads(json_path.read_text(encoding="utf-8"))), dest)
    print(f"resultado: {json_path}")
    print(f"relatorio: {relatorio}")


if __name__ == "__main__":
    main()

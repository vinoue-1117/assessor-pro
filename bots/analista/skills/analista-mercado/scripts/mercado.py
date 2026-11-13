# mercado.py v3
"""Consulta de mercado via yfinance, taxas do Banco Central (SGS) e do Tesouro Direto.

Subcomandos: cotacao, historico, opcoes, taxa, tesouro.
Saida: JSON no stdout. Erro: objeto com "erro" e "consultado_em", exit code != 0.
Nao inventa dado.
"""
import argparse
import csv
import io
import json
import logging
import math
import re
import sys
import urllib.request
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

try:
    TZ = ZoneInfo("America/Sao_Paulo")
except ZoneInfoNotFoundError:
    # Brasil sem horario de verao desde 2019: o offset fixo so entra se faltar o tzdb.
    TZ = timezone(timedelta(hours=-3))

B3 = re.compile(r"^[A-Z]{4}\d{1,2}$")
YF_INTERVALO = {"1d": "1d", "1w": "1wk", "1m": "1mo", "1h": "1h"}
CAMPOS_PRECO = {"open", "high", "low", "close", "adj close", "volume"}
SGS = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json&dataInicial={de}&dataFinal={ate}"
# Series do SGS (Banco Central) por indicador: (campo, codigo, unidade).
TAXAS = {
    "selic": [("meta", 432, "% a.a."), ("efetiva", 1178, "% a.a. (base 252)")],
    "cdi": [("taxa", 4389, "% a.a. (base 252)")],
    "ipca": [("mes", 433, "% no mês"), ("acumulado_12m", 13522, "% em 12 meses")],
}
# O IPCA e mensal e sai com atraso: a janela precisa alcancar o ultimo mes publicado.
JANELA_SGS = 100
# Historico completo do Tesouro Direto num CSV so (cerca de 15 MB): o servidor nao atende pedido de faixa.
TESOURO = (
    "https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3"
    "/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/PrecoTaxaTesouroDireto.csv"
)
COLUNAS_TESOURO = {
    "titulo": "Tipo Titulo",
    "vencimento": "Data Vencimento",
    "taxa_compra": "Taxa Compra Manha",
    "taxa_venda": "Taxa Venda Manha",
    "pu_compra": "PU Compra Manha",
    "pu_venda": "PU Venda Manha",
}


class FonteErro(Exception):
    pass


def agora():
    return datetime.now(TZ).isoformat(timespec="seconds")


def erro(msg, **extra):
    return {"erro": msg, "consultado_em": agora(), **extra}


def normalizar(ticker):
    """B3 `^[A-Z]{4}\\d{1,2}$` ganha `.SA`. Indice `^...`, cambio `=X` e o resto ficam."""
    t = ticker.strip().upper()
    if t.startswith("^") or t.endswith("=X") or t.endswith(".SA"):
        return t
    if B3.match(t):
        return t + ".SA"
    return t


def num(valor, casas=4):
    if valor is None or isinstance(valor, bool):
        return None
    try:
        f = float(valor)
    except (TypeError, ValueError):
        return None
    if math.isnan(f) or math.isinf(f):
        return None
    return round(f, casas)


def inteiro(valor):
    f = num(valor, 8)
    if f is None:
        return None
    return int(f)


def texto(valor):
    if valor is None:
        return None
    s = str(valor).strip()
    if not s or s.lower() == "nan":
        return None
    return s


def modulo_yf():
    try:
        import yfinance as yf
    except ImportError as e:
        raise FonteErro("yfinance não está instalado") from e
    logging.getLogger("yfinance").setLevel(logging.CRITICAL)
    return yf


def abrir(sym):
    return modulo_yf().Ticker(sym)


def _niveis(cols):
    if hasattr(cols, "nlevels") and getattr(cols, "nlevels", 1) > 1 and hasattr(cols, "get_level_values"):
        return [list(cols.get_level_values(i)) for i in range(cols.nlevels)]
    seq = list(cols)
    if seq and all(isinstance(c, tuple) for c in seq):
        n = max(len(c) for c in seq)
        return [[c[i] if i < len(c) else "" for c in seq] for i in range(n)]
    return None


def achatar(df):
    """Desce o MultiIndex do yfinance quando um dos niveis e Open/High/Low/Close/Volume."""
    if df is None:
        return df
    niveis = _niveis(df.columns)
    if not niveis:
        return df
    escolhido = None
    for i, vals in enumerate(niveis):
        if any(str(v).strip().lower() in CAMPOS_PRECO for v in vals):
            escolhido = i
            break
    if escolhido is None:
        return df
    out = df.copy() if hasattr(df, "copy") else df
    out.columns = [str(v).strip() for v in niveis[escolhido]]
    return out


def pegar(row, *nomes):
    if isinstance(row, dict):
        pares = row.items()
    else:
        try:
            pares = ((k, row[k]) for k in row.index)
        except Exception:
            return None
    chaves = {str(k).strip().lower(): v for k, v in pares}
    for nome in nomes:
        if nome.lower() in chaves:
            return chaves[nome.lower()]
    return None


def registros(df):
    df = achatar(df)
    if df is None or getattr(df, "empty", True):
        return []
    linhas = []
    for _, row in df.iterrows():
        if isinstance(row, dict):
            linhas.append(dict(row))
        else:
            linhas.append({k: row[k] for k in row.index})
    return linhas


def barras(df):
    df = achatar(df)
    if df is None or getattr(df, "empty", True):
        return []
    out = []
    for idx, row in df.iterrows():
        fech = num(pegar(row, "Close"))
        if fech is None:
            fech = num(pegar(row, "Adj Close"))
        out.append({
            "idx": idx,
            "abertura": num(pegar(row, "Open")),
            "maxima": num(pegar(row, "High")),
            "minima": num(pegar(row, "Low")),
            "fechamento": fech,
            "volume": inteiro(pegar(row, "Volume")),
        })
    return out


def formata_quando(idx, intervalo):
    if hasattr(idx, "to_pydatetime"):
        try:
            idx = idx.to_pydatetime()
        except Exception:
            pass
    if isinstance(idx, datetime) and idx.tzinfo is not None:
        try:
            idx = idx.astimezone(TZ)
        except Exception:
            pass
    texto_idx = idx.isoformat() if hasattr(idx, "isoformat") else str(idx)
    if intervalo == "1h":
        return texto_idx
    return texto_idx[:10]


def metadados(tk):
    nome = moeda = None
    try:
        info = tk.info
    except Exception:
        info = None
    if isinstance(info, dict):
        bruto = info.get("shortName") or info.get("short_name")
        nome = texto(bruto)
        moeda = texto(info.get("currency"))
    if not moeda:
        try:
            fi = tk.fast_info
        except Exception:
            fi = None
        if isinstance(fi, dict):
            moeda = texto(fi.get("currency"))
        elif fi is not None:
            try:
                moeda = texto(getattr(fi, "currency", None))
            except Exception:
                moeda = None
    return nome, moeda


def intervalo_datas(de_s, ate_s):
    hoje = datetime.now(TZ).date()
    try:
        ate = date.fromisoformat(ate_s) if ate_s else hoje
        de = date.fromisoformat(de_s) if de_s else ate - timedelta(days=30)
    except ValueError:
        raise FonteErro("data inválida (use YYYY-MM-DD)")
    if de > ate:
        raise FonteErro("--de é posterior a --ate")
    return de, ate


def cotacao_uma(ticker):
    rot = ticker.strip().upper()
    sym = normalizar(rot)
    try:
        tk = abrir(sym)
        rows = [b for b in barras(tk.history(period="10d", interval="1d", auto_adjust=False)) if b["fechamento"] is not None]
        if not rows:
            raise FonteErro(f"yfinance sem dados para {sym}")
        u = rows[-1]
        prev = rows[-2]["fechamento"] if len(rows) > 1 else None
        var = None
        if prev not in (None, 0):
            var = round((u["fechamento"] / prev - 1) * 100, 3)
        nome, moeda = metadados(tk)
        return {
            "ticker": rot,
            "ticker_yf": sym,
            "preco": u["fechamento"],
            "variacao_pct": var,
            "abertura": u["abertura"],
            "maxima": u["maxima"],
            "minima": u["minima"],
            "volume": u["volume"],
            "moeda": moeda,
            "nome": nome,
            "data_pregao": formata_quando(u["idx"], "1d"),
            "fonte": "yfinance",
            "atraso_estimado_min": 15,
            "consultado_em": agora(),
        }
    except FonteErro as e:
        return erro(str(e), ticker=rot, ticker_yf=sym)
    except Exception as e:
        return erro(f"yfinance falhou para {sym}: {type(e).__name__}: {e}", ticker=rot, ticker_yf=sym)


def cmd_cotacao(a):
    return [cotacao_uma(t) for t in a.tickers]


def cmd_historico(a):
    rot = a.ticker.strip().upper()
    sym = normalizar(rot)
    if a.intervalo not in YF_INTERVALO:
        return erro(f"intervalo inválido: {a.intervalo} (use 1d, 1w, 1m ou 1h)", ticker=rot)
    try:
        de, ate = intervalo_datas(a.de, a.ate)
    except FonteErro as e:
        return erro(str(e), ticker=rot)
    try:
        tk = abrir(sym)
        df = tk.history(
            start=de.isoformat(),
            end=(ate + timedelta(days=1)).isoformat(),
            interval=YF_INTERVALO[a.intervalo],
            auto_adjust=False,
        )
        dados = []
        for b in barras(df):
            if b["fechamento"] is None:
                continue
            dados.append({
                "data": formata_quando(b["idx"], a.intervalo),
                "abertura": b["abertura"],
                "maxima": b["maxima"],
                "minima": b["minima"],
                "fechamento": b["fechamento"],
                "volume": b["volume"],
            })
        if not dados:
            raise FonteErro(f"yfinance sem histórico para {sym}")
        return {
            "ticker": rot,
            "ticker_yf": sym,
            "intervalo": a.intervalo,
            "de": de.isoformat(),
            "ate": ate.isoformat(),
            "fonte": "yfinance",
            "atraso_estimado_min": 15,
            "consultado_em": agora(),
            "dados": dados,
        }
    except FonteErro as e:
        return erro(str(e), ticker=rot, ticker_yf=sym)
    except Exception as e:
        return erro(f"yfinance falhou para {sym}: {type(e).__name__}: {e}", ticker=rot, ticker_yf=sym)


def ler_opcoes(df, tipo, vencimento):
    saida = []
    for row in registros(df):
        iv = num(pegar(row, "impliedVolatility"), 8)
        saida.append({
            "codigo": texto(pegar(row, "contractSymbol")),
            "tipo": tipo,
            "strike": num(pegar(row, "strike")),
            "vencimento": vencimento,
            "premio_ultimo": num(pegar(row, "lastPrice")),
            "bid": num(pegar(row, "bid")),
            "ask": num(pegar(row, "ask")),
            "volume": inteiro(pegar(row, "volume")),
            "iv_pct": None if iv is None else round(iv * 100, 2),
        })
    return saida


def cmd_opcoes(a):
    rot = a.subjacente.strip().upper()
    sym = normalizar(rot)
    if sym.endswith(".SA"):
        return erro(
            f"yfinance não fornece cadeia de opções da B3 ({sym}). "
            "Opções da B3 não vêm por esta fonte.",
            ticker=rot,
            ticker_yf=sym,
        )
    tipo = a.tipo.upper() if a.tipo else None
    try:
        tk = abrir(sym)
        vencs = [str(v) for v in (getattr(tk, "options", None) or [])]
        if not vencs:
            raise FonteErro(f"yfinance sem cadeia de opções para {sym}")
        if a.vencimento and a.vencimento not in vencs:
            amostra = ", ".join(vencs[:8])
            raise FonteErro(f"vencimento {a.vencimento} não existe no yfinance; disponíveis: {amostra}")
        v = a.vencimento or vencs[0]
        chain = tk.option_chain(v)
        lst = ler_opcoes(getattr(chain, "calls", None), "CALL", v)
        lst += ler_opcoes(getattr(chain, "puts", None), "PUT", v)
        if tipo:
            lst = [o for o in lst if o["tipo"] == tipo]
        if a.so_negociadas:
            lst = [o for o in lst if (o.get("volume") or 0) > 0]
        lst.sort(key=lambda o: (o["tipo"], o["strike"] if o["strike"] is not None else 0, o["codigo"] or ""))
        return {
            "subjacente": rot,
            "ticker_yf": sym,
            "vencimento": v,
            "vencimentos_disponiveis": vencs,
            "fonte": "yfinance",
            "atraso_estimado_min": 15,
            "consultado_em": agora(),
            "opcoes": lst,
        }
    except FonteErro as e:
        return erro(str(e), ticker=rot, ticker_yf=sym)
    except Exception as e:
        return erro(f"yfinance falhou para {sym}: {type(e).__name__}: {e}", ticker=rot, ticker_yf=sym)


def baixar_sgs(codigo, de, ate):
    url = SGS.format(codigo=codigo, de=de.strftime("%d/%m/%Y"), ate=ate.strftime("%d/%m/%Y"))
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def ultimo_sgs(codigo, hoje):
    """Ultimo valor com data ate hoje.

    A meta Selic vem preenchida ate a proxima reuniao do Copom, e a ordem das
    datas varia entre series: por isso o filtro e o max, nunca a ultima linha.
    """
    vistos = []
    for linha in baixar_sgs(codigo, hoje - timedelta(days=JANELA_SGS), hoje):
        try:
            dia = datetime.strptime(str(linha["data"]), "%d/%m/%Y").date()
        except (KeyError, TypeError, ValueError):
            continue
        valor = num(linha.get("valor"))
        if valor is not None and dia <= hoje:
            vistos.append((dia, valor))
    if not vistos:
        raise FonteErro(f"BCB sem dados para a série {codigo}")
    dia, valor = max(vistos)
    return dia.isoformat(), valor


def taxa_uma(nome):
    ind = nome.strip().lower()
    if ind not in TAXAS:
        return erro(f"indicador inválido: {nome} (use selic, cdi ou ipca)", indicador=ind)
    hoje = datetime.now(TZ).date()
    try:
        out = {"indicador": ind}
        for campo, codigo, unidade in TAXAS[ind]:
            dia, valor = ultimo_sgs(codigo, hoje)
            out[campo] = {"valor": valor, "unidade": unidade, "data": dia, "serie_sgs": codigo}
        out["fonte"] = "bcb-sgs"
        out["consultado_em"] = agora()
        return out
    except FonteErro as e:
        return erro(str(e), indicador=ind)
    except Exception as e:
        return erro(f"BCB falhou para {ind}: {type(e).__name__}: {e}", indicador=ind)


def cmd_taxa(a):
    return [taxa_uma(n) for n in a.indicadores]


def baixar_tesouro():
    with urllib.request.urlopen(TESOURO, timeout=90) as r:
        return r.read().decode("latin-1")


def data_br(texto_data):
    return datetime.strptime(texto_data.strip(), "%d/%m/%Y").date().isoformat()


def ler_tesouro(bruto, filtro):
    """Titulos da data-base mais recente do CSV. A ordem das linhas nao e garantida."""
    leitor = csv.DictReader(io.StringIO(bruto), delimiter=";")
    faltam = [c for c in ["Data Base", *COLUNAS_TESOURO.values()] if c not in (leitor.fieldnames or [])]
    if faltam:
        raise FonteErro("o CSV do Tesouro Transparente mudou de formato: falta " + ", ".join(faltam))
    por_dia = {}
    for linha in leitor:
        try:
            dia = data_br(linha["Data Base"] or "")
        except ValueError:
            continue
        por_dia.setdefault(dia, []).append(linha)
    if not por_dia:
        raise FonteErro("o CSV do Tesouro Transparente veio sem linha de dado")
    data_base = max(por_dia)
    titulos = []
    for linha in por_dia[data_base]:
        item = {"titulo": texto(linha["Tipo Titulo"]), "vencimento": data_br(linha["Data Vencimento"])}
        for campo in ("taxa_compra", "taxa_venda", "pu_compra", "pu_venda"):
            item[campo] = num((linha[COLUNAS_TESOURO[campo]] or "").replace(",", "."))
        titulos.append(item)
    tipos = sorted({t["titulo"] for t in titulos if t["titulo"]})
    if filtro:
        titulos = [t for t in titulos if filtro in (t["titulo"] or "").lower()]
        if not titulos:
            raise FonteErro(f"nenhum título com '{filtro}' em {data_base}; tipos: " + ", ".join(tipos))
    titulos.sort(key=lambda t: (t["titulo"] or "", t["vencimento"]))
    return data_base, titulos


def cmd_tesouro(a):
    filtro = (a.tipo or "").strip().lower()
    try:
        data_base, titulos = ler_tesouro(baixar_tesouro(), filtro)
        return {
            "data_base": data_base,
            "unidade_taxa": "% a.a.",
            "fonte": "tesouro-transparente",
            "consultado_em": agora(),
            "titulos": titulos,
        }
    except FonteErro as e:
        return erro(str(e))
    except Exception as e:
        return erro(f"Tesouro Transparente falhou: {type(e).__name__}: {e}")


def tem_erro(r):
    if isinstance(r, list):
        return any(tem_erro(x) for x in r)
    return isinstance(r, dict) and "erro" in r


def main(argv=None):
    p = argparse.ArgumentParser(prog="mercado.py", description="Consulta de mercado via yfinance, taxas do Banco Central e do Tesouro Direto. Saída JSON.")
    sp = p.add_subparsers(dest="cmd", required=True)

    c = sp.add_parser("cotacao", help="preço, variação, volume, moeda e nome")
    c.add_argument("tickers", nargs="+")
    c.set_defaults(fn=cmd_cotacao)

    h = sp.add_parser("historico", help="OHLCV")
    h.add_argument("ticker")
    h.add_argument("--de", help="YYYY-MM-DD (padrão: 30 dias antes de --ate)")
    h.add_argument("--ate", help="YYYY-MM-DD (padrão: hoje em America/Sao_Paulo)")
    h.add_argument("--intervalo", default="1d", help="1d (padrão), 1w, 1m ou 1h")
    h.set_defaults(fn=cmd_historico)

    o = sp.add_parser("opcoes", help="cadeia de opções via yfinance (EUA; B3 devolve erro)")
    o.add_argument("subjacente")
    o.add_argument("--vencimento", help="YYYY-MM-DD (padrão: o primeiro da cadeia)")
    o.add_argument("--tipo", choices=["CALL", "PUT", "call", "put"])
    o.add_argument("--so-negociadas", action="store_true")
    o.set_defaults(fn=cmd_opcoes)

    t = sp.add_parser("taxa", help="Selic, CDI e IPCA pelo SGS do Banco Central")
    t.add_argument("indicadores", nargs="+", help="selic, cdi ou ipca")
    t.set_defaults(fn=cmd_taxa)

    td = sp.add_parser("tesouro", help="taxas e preços do Tesouro Direto na data-base mais recente")
    td.add_argument("--tipo", help="trecho do nome do título (ex.: ipca+, prefixado, selic)")
    td.set_defaults(fn=cmd_tesouro)

    a = p.parse_args(argv)
    try:
        res = a.fn(a)
    except Exception as e:
        res = erro(f"{type(e).__name__}: {e}")
    print(json.dumps(res, ensure_ascii=False, indent=1, default=str))
    sys.exit(1 if tem_erro(res) else 0)


if __name__ == "__main__":
    main()

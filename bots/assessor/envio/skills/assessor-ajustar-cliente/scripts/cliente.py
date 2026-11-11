#!/usr/bin/env python3
# cliente.py v1 | uso: python3 cliente.py PLANILHA add CONTA TELEFONE NOME [APELIDO] | set CONTA CAMPO VALOR | rm CONTA
import csv,io,re,sys,zipfile
from datetime import datetime
from pathlib import Path
COLS=('conta_xp','telefone','nome','apelido')
DDD={11,12,13,14,15,16,17,18,19,21,22,24,27,28,31,32,33,34,35,37,38,41,42,43,44,45,46,47,48,49,51,53,54,55,61,62,63,64,65,66,67,68,69,71,73,74,75,77,79,81,82,83,84,85,86,87,88,89,91,92,93,94,95,96,97,98,99}
def die(msg):
    sys.exit(msg)
def ler_planilha(p):
    p=Path(p)
    if p.suffix.lower()=='.xlsx':
        z=zipfile.ZipFile(p);x=lambda n:z.read(n).decode()
        ss=[re.sub(r'<[^>]+>','',s) for s in re.findall(r'<si>(.*?)</si>',x('xl/sharedStrings.xml'),re.S)] if 'xl/sharedStrings.xml' in z.namelist() else []
        rows=[]
        for r in re.findall(r'<row[^>]*>(.*?)</row>',x('xl/worksheets/sheet1.xml'),re.S):
            d={}
            for ref,a,v in re.findall(r'<c r="([A-Z]+)\d+"([^>]*?)(?:/>|>(.*?)</c>)',r,re.S):
                v=re.sub(r'<[^>]+>','',v or '');d[ref]=ss[int(v)] if 't="s"' in a and v else re.sub(r'\.0$','',v)
            rows.append(d)
        cols=sorted({c for d in rows for c in d},key=lambda c:(len(c),c))
        rows=[[d.get(c,'') for c in cols] for d in rows]
    else:
        b=p.read_bytes()
        try:s=b.decode('utf-8-sig')
        except UnicodeDecodeError:s=b.decode('cp1252')
        rows=list(csv.reader(io.StringIO(s),delimiter=';' if s.split('\n')[0].count(';')>s.split('\n')[0].count(',') else ','))
    if not rows:die('planilha vazia')
    h=[c.strip().lower() for c in rows[0]]
    falta=[c for c in COLS if c not in h]
    if falta:die('planilha sem colunas: '+', '.join(falta))
    return [{c:(r[h.index(c)] if h.index(c)<len(r) else '').strip() for c in COLS} for r in rows[1:] if any(r)]
def digitos(s):
    return re.sub(r'\D','',s or '')
def conta_ok(s):
    s=(s or '').strip()
    if not s or not s.isdigit():die('conta inválida: use só dígitos')
    return s
def normalizar_telefone(s):
    bruto=(s or '').strip()
    d=digitos(bruto)
    if d.startswith('00'):d=d[2:]
    elif d.startswith('0'):d=d[1:]
    if d.startswith('550') and len(d) in (13,14):d='55'+d[3:]
    if d.startswith('55') and len(d) in (12,13):
        nac=d[2:]
    elif len(d) in (10,11):
        nac=d
    else:
        die(f'telefone inválido: "{bruto}" — informe DDD + número, com ou sem 55 (ex.: 11 9xxxx-xxxx)')
    ddd,num=nac[:2],nac[2:]
    if int(ddd) not in DDD:die(f'telefone inválido: DDD {ddd} não existe')
    if len(num)==9 and not num.startswith('9'):die(f'telefone inválido: celular com DDD {ddd} deve começar com 9')
    if len(num)==8 and num[0] not in '2345':die(f'telefone inválido: "{bruto}" não é fixo (8 dígitos, inicia 2–5) nem celular (9 dígitos começando com 9) depois do DDD {ddd}')
    return '+55'+ddd+num
def chave(linha):
    return digitos(linha['conta_xp'])
def achar(linhas,conta):
    ixs=[i for i,l in enumerate(linhas) if chave(l)==conta]
    if not ixs:die(f'conta {conta} não encontrada')
    if len(ixs)>1:die(f'conta {conta} repetida na planilha; não altero até ficar única')
    return ixs[0]
def linha_txt(l):
    return ' | '.join(l[c] for c in COLS) if l else '(nenhuma)'
def ativos(pasta):
    out=[]
    for p in pasta.iterdir():
        if not p.is_file():continue
        n=p.name.lower()
        if n.startswith('clientes.bak-'):continue
        if n in ('clientes.csv','clientes.xlsx'):out.append(p)
    return out
def bak(pasta,ext):
    selo=datetime.now().strftime('%Y%m%d-%H%M')
    ext=ext if ext.startswith('.') else '.'+ext
    cand=pasta/f'clientes.bak-{selo}{ext}'
    n=2
    while cand.exists():
        cand=pasta/f'clientes.bak-{selo}-{n}{ext}';n+=1
    return cand
def gravar(pasta,linhas):
    tmp=pasta/'.clientes.csv.tmp'
    with tmp.open('w',newline='',encoding='utf-8') as fh:
        w=csv.writer(fh);w.writerow(COLS);w.writerows([[l[c] for c in COLS] for l in linhas])
    guardados=[]
    for p in ativos(pasta):
        dest=bak(pasta,p.suffix.lower());p.rename(dest);guardados.append(dest)
    final=pasta/'clientes.csv'
    tmp.replace(final)
    for g in guardados:print(f'backup: {g}')
    print(f'gravado: {final}')
def uso():
    die('uso: python3 cliente.py PLANILHA add CONTA TELEFONE NOME [APELIDO] | set CONTA CAMPO VALOR | rm CONTA')
def main(argv):
    if len(argv)<3:uso()
    planilha=Path(argv[1])
    if not planilha.is_file():die(f'planilha não encontrada: {planilha}')
    if planilha.name.lower() not in ('clientes.csv','clientes.xlsx'):die('use a planilha ativa clientes.csv ou clientes.xlsx')
    cmd=argv[2].lower()
    linhas=ler_planilha(planilha)
    if cmd=='add':
        if len(argv) not in (6,7):uso()
        conta=conta_ok(argv[3]);tel=normalizar_telefone(argv[4]);nome=argv[5].strip();apelido=argv[6].strip() if len(argv)==7 else ''
        if not nome:die('nome obrigatório')
        if any(chave(l)==conta for l in linhas):die(f'conta {conta} já existe')
        antes=None
        depois={'conta_xp':conta,'telefone':tel,'nome':nome,'apelido':apelido}
        linhas.append(depois)
    elif cmd=='set':
        if len(argv)<6:uso()
        conta=conta_ok(argv[3]);campo=argv[4].strip().lower();valor=' '.join(argv[5:]).strip()
        if campo not in COLS:die('campo inválido: use conta_xp, telefone, nome ou apelido')
        i=achar(linhas,conta);antes=dict(linhas[i]);depois=dict(antes)
        if campo=='conta_xp':
            nova=conta_ok(valor)
            if any(j!=i and chave(l)==nova for j,l in enumerate(linhas)):die(f'conta {nova} já existe')
            depois['conta_xp']=nova
        elif campo=='telefone':depois['telefone']=normalizar_telefone(valor)
        elif campo=='nome':
            if not valor:die('nome obrigatório')
            depois['nome']=valor
        else:depois['apelido']=valor
        linhas[i]=depois
    elif cmd=='rm':
        if len(argv)!=4:uso()
        conta=conta_ok(argv[3]);i=achar(linhas,conta);antes=linhas.pop(i);depois=None
    else:uso()
    print('antes: '+linha_txt(antes))
    print('depois: '+linha_txt(depois))
    if antes==depois and len(ativos(planilha.parent))<=1:
        print('sem mudança')
        return
    gravar(planilha.parent,linhas)
if __name__=='__main__':main(sys.argv)

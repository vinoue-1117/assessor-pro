#!/usr/bin/env python3
# xpp.py v1 | uso: python3 xpp.py LOTE.zip CLIENTES.csv|.xlsx DISCURSO.txt  (requer pdftotext/poppler)
import csv,io,re,sys,shutil,zipfile,subprocess,unicodedata as U
from pathlib import Path
from collections import Counter
MESES='janeiro fevereiro março abril maio junho julho agosto setembro outubro novembro dezembro'.split()
P=r'-?\d{1,3}(?:\.\d{3})*,\d{2}%';R=r'-?R\$ ?\d{1,3}(?:\.\d{3})*,\d{2}'
CAMPOS={'patrimonio':('PATRIMÔNIO TOTAL BRUTO:',R),'cart_mes':('RENTABILIDADE MÊS:',P),'resultado':('GANHO MÊS:',R),
 'meses_pos':('Meses Positivos',r'\d+'),'meses_cdi':('Meses Acima do CDI',r'\d+')}
IND={'Portfólio':'cart','CDI':'cdi','Ibovespa':'ibov','IPCA':'ipca'}
MODELO="""Olá, {apelido}!

Fechamos {mes_ano}. Segue em anexo seu relatório *XPerformance* completo (PDF); aqui vai o resumo:

📊 *No mês*
• Carteira: *{cart_mes}*
• CDI: {cdi_mes}
• Ibovespa: {ibov_mes}
• IPCA: {ipca_mes}

📈 *No ano / 12M / 24M*
• Carteira: {cart_ano} / {cart_12m} / {cart_24m}
• CDI: {cdi_ano} / {cdi_12m} / {cdi_24m}
• Ibovespa: {ibov_ano} / {ibov_12m} / {ibov_24m}

💰 Resultado financeiro no mês: *{resultado}*
🏦 Patrimônio total bruto: *{patrimonio}*
Nos últimos 24 meses, {meses_pos} meses positivos e {meses_cdi} acima do CDI.

🌎 *Cenário do mês:* {discurso_macro}

Qualquer dúvida sobre o relatório, é só me chamar.

Abraço!"""
norm=lambda s:U.normalize('NFKD',s or '').encode('ascii','ignore').decode().strip().lower()
def ler_pdf(pdf):
    t=subprocess.run(['pdftotext','-raw','-f','1','-l','2',str(pdf),'-'],capture_output=True,text=True).stdout.replace('\xa0',' ')
    f,err={},[]
    m=re.search(r'Data de Refer\w+\n(\d+) .*?(\d\d)/(\d\d)/(\d{4})',t)
    if m:f['conta'],f['data']=m[1],(m[4],m[3],m[2])
    else:err.append('capa (conta/data)')
    for k,(rot,rx) in CAMPOS.items():
        m=re.search(re.escape(rot)+r'\n('+rx+r')\n',t)
        if m:f[k]=m[1]
        else:err.append(k)
    for nome,k in IND.items():
        m=re.search(r'^'+nome+' '+' '.join(['('+P+')']*4)+'$',t,re.M)
        if m:f.update({k+'_mes':m[1],k+'_ano':m[2],k+'_12m':m[3],k+'_24m':m[4]})
        else:err.append('referências '+nome)
    return f,err
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
    h=[c.strip().lower() for c in rows[0]]
    falta=[c for c in ('conta_xp','telefone','nome','apelido') if c not in h]
    if falta:sys.exit('planilha sem colunas: '+', '.join(falta))
    return [{c:(r[h.index(c)] if h.index(c)<len(r) else '').strip() for c in ('conta_xp','telefone','nome','apelido')} for r in rows[1:] if any(r)]
def main(zp,planilha,disc):
    discurso=' '.join(l.strip() for l in Path(disc).read_text(encoding='utf-8-sig').splitlines() if l.strip() and not l.lstrip().startswith(('#','<!--')))
    if not discurso:sys.exit('discurso macro vazio')
    base=Path('/workspace/xpp');tmp=base/'_pdfs';shutil.rmtree(tmp,ignore_errors=True)
    pdfs={};dup=[];nomes={}
    with zipfile.ZipFile(zp) as z:
        for n in z.namelist():
            if not n.lower().endswith('.pdf'):continue
            d=tmp/Path(n).name;d.parent.mkdir(parents=True,exist_ok=True);d.write_bytes(z.read(n))
            m=re.search(r'XPerformance - (\d+) (.+?) - Ref',d.name);f,err=ler_pdf(d)
            c=f.get('conta') or (m and m[1]) or d.stem
            if m and f.get('conta') and m[1]!=f['conta']:err.append(f'conta do arquivo {m[1]} difere da capa')
            if c in pdfs:dup.append(c)
            pdfs[c]=(d,f,err);nomes[c]=m[2] if m else ''
    datas=Counter(f['data'] for _,f,_ in pdfs.values() if 'data' in f)
    if not datas:sys.exit('nenhum PDF XPerformance legível no zip')
    a,me,di=datas.most_common(1)[0][0];ref=f'{a}-{me}-{di}';out=base/f'lote-{ref}'
    shutil.rmtree(out,ignore_errors=True);out.mkdir(parents=True)
    linhas=ler_planilha(planilha);cont=Counter(re.sub(r'\D','',l['conta_xp']) for l in linhas);res=[]
    for l in linhas:
        c=re.sub(r'\D','',l['conta_xp']);bloq,rev=[],[]
        if cont[c]>1:bloq.append('conta repetida na planilha')
        tel=re.sub(r'\D','',l['telefone'])
        if not tel:bloq.append('sem telefone')
        elif len(tel)<10:bloq.append('telefone inválido')
        ap=l['apelido']
        if not ap:ap=(l['nome'].split() or [''])[0];rev.append(f'sem apelido, usado "{ap}"')
        if c not in pdfs:bloq.append('sem PDF no lote')
        else:
            d,f,err=pdfs.pop(c)
            if err:bloq.append('não lido: '+', '.join(err))
            if f.get('data',(a,me,di))!=(a,me,di):bloq.append('data de referência diferente do lote')
            if c in dup:rev.append('conta repetida no zip')
            nn=norm(l['nome']).split()
            if nomes[c] and (not nn or norm(nomes[c]).split()[0]!=nn[0]):rev.append(f'nome no PDF "{nomes[c]}" ≠ planilha "{l["nome"]}"')
            if not err:
                msg=MODELO.format(apelido=ap,mes_ano=f'{MESES[int(me)-1]}/{a}',discurso_macro=discurso,**f)
                if len(msg)>1024:rev.append(f'mensagem com {len(msg)} caracteres (legenda do WhatsApp aceita 1024)')
                p=out/c;p.mkdir();shutil.copy(d,p/'relatorio.pdf');(p/'mensagem.txt').write_text(msg,encoding='utf-8')
        res.append([c,l['nome'],ap,'+'+tel if tel else '','bloqueado' if bloq else 'revisar' if rev else 'pronto','; '.join(bloq+rev)])
    for c,(d,f,err) in pdfs.items():res.append([c,nomes[c],'','','bloqueado','PDF sem linha na planilha'])
    with open(out/'lote.csv','w',newline='',encoding='utf-8') as fh:
        w=csv.writer(fh);w.writerow(['conta_xp','nome','apelido','telefone','status','problema']);w.writerows(res)
    shutil.rmtree(tmp,ignore_errors=True)
    print(f'LOTE {ref} -> {out}');print(dict(Counter(r[4] for r in res)))
    for r in res:
        if r[5]:print(f'{r[0]} {r[1]}: {r[4]} - {r[5]}')
if __name__=='__main__':main(*sys.argv[1:4])

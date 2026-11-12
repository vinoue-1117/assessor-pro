#!/usr/bin/env python3
# assessor.py v7 | uso: python3 assessor.py LOTE.zip CLIENTES.csv|.xlsx DISCURSO.md  (requer pdftotext/poppler)
#   python3 assessor.py importar PLANILHA | aprovar REF CODIGO [CONTA_REVISAR ...] | checar [REF] | registrar REF CONTA STATUS [HH:MM]
#   python3 assessor.py copiar REF CONTA | copiar CAMINHO.txt | marcar | conferir-caixa REF CONTA | conferir-caixa CAMINHO.txt
#   copiar/conferir-caixa: 1 argumento = caminho do .txt (o que o bot de WhatsApp recebe); 2 = REF CONTA.
#   Trava de texto: copiar, Ctrl+V na caixa, marcar, Ctrl+A e Ctrl+C na caixa, conferir-caixa.
#   Área de transferência X11 (xclip -selection clipboard) no DISPLAY do ambiente: tem que ser o display do desktop do bot.
import csv,io,os,re,sys,json,shutil,hashlib,zipfile,subprocess,unicodedata as U
from datetime import datetime
from pathlib import Path
from collections import Counter
BASE=Path(os.environ.get('ASSESSOR_BASE','/workspace/assessor'))
CAB_LOTE=['conta_xp','nome','apelido','telefone','status','problema','aviso']
CAB_ENVIOS=['data','ref','conta_xp','apelido','status','horario']
STATUS_ENVIO=r'(enviado|(falhou|pulado|teste): .+)'
COLUNAS={'conta_xp':{'contaxp','conta','numerodaconta','numeroconta','ndaconta','nconta','contacliente','codigodaconta'},
 'telefone':{'telefone','celular','whatsapp','whats','zap','fone','tel','telefonecelular','numerowhatsapp','numerodowhatsapp'},
 'nome':{'nome','cliente','nomedocliente','nomecliente','nomecompleto'},
 'apelido':{'apelido','comochamar','tratamento','vocativo','primeironome'}}
DDD={11,12,13,14,15,16,17,18,19,21,22,24,27,28,31,32,33,34,35,37,38,41,42,43,44,45,46,47,48,49,51,53,54,55,61,62,63,64,65,66,67,68,69,71,73,74,75,77,79,81,82,83,84,85,86,87,88,89,91,92,93,94,95,96,97,98,99}
MESES='janeiro fevereiro março abril maio junho julho agosto setembro outubro novembro dezembro'.split()
P=r'-?\d{1,3}(?:\.\d{3})*,\d{2}%';R=r'-?R\$ ?\d{1,3}(?:\.\d{3})*,\d{2}'
CAMPOS={'patrimonio':('PATRIMÔNIO TOTAL BRUTO:',R),'cart_mes':('RENTABILIDADE MÊS:',P),'resultado':('GANHO MÊS:',R)}
IND={'Portfólio':'cart','CDI':'cdi','Ibovespa':'ibov','IPCA':'ipca'}
JANELAS={'ano':'No ano','12m':'12M'}
MODELO="""Olá, {apelido}!

Segue seu relatório de {mes_ano}. Resumo:

📊 *No mês*
• Carteira: *{cart_mes}*
• CDI: {cdi_mes} | Ibovespa: {ibov_mes} | IPCA: {ipca_mes}

{janelas}💰 Resultado no mês: *{resultado}*
🏦 Patrimônio bruto: *{patrimonio}*

🌎 *Cenário do mês*
{discurso_macro}

Qualquer dúvida, é só me chamar. Abraço!"""
LIMITE_MSG=1024# legenda de anexo do WhatsApp: o que passa disso é cortado
TETO_DISCURSO=550# deixa a mensagem inteira abaixo de LIMITE_MSG com os números de qualquer cliente
tam=lambda s:len(s.encode('utf-16-le'))//2# emoji conta 2: lado seguro, o limite foi medido só com letras e números
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
    v='(?:'+P+'|-)'# conta sem histórico traz "-" em ano, 12M ou 24M; o mês é obrigatório
    for nome,k in IND.items():
        # Ibovespa e IPCA entram na mensagem só com o mês: o resto da linha não é exigido
        m=re.search(r'^'+nome+' ('+P+')'+(f' ({v}) ({v}) {v}$' if k in('cart','cdi') else ''),t,re.M)
        if m:f.update(zip((k+'_mes',k+'_ano',k+'_12m'),m.groups()))
        else:err.append('referências '+nome)
    for j in cobertas(f):
        if f.get('cdi_'+j)=='-':err.append('referências CDI sem '+JANELAS[j].split()[-1])
    return f,err
def cobertas(f):
    """Janelas em que a carteira tem rentabilidade: as que a leitura confere no CDI e as que entram na mensagem."""
    return [j for j in JANELAS if f.get('cart_'+j,'-')!='-']
def janelas(f):
    """Bloco "No ano / 12M" só com as janelas em que a carteira tem rentabilidade: sem a carteira, o CDI da janela cobre outro período."""
    js=cobertas(f)
    if not js:return ''
    lin=lambda k:' / '.join(f[k+'_'+j] for j in js)
    return f"📈 *{' / '.join(JANELAS[j] for j in js)}*\n• Carteira: {lin('cart')}\n• CDI: {lin('cdi')}\n\n"
def ler_planilha(p):
    p=Path(p)
    if p.suffix.lower()=='.xlsx':
        z=zipfile.ZipFile(p);x=lambda n:z.read(n).decode()
        ss=[re.sub(r'<[^>]+>','',s) for s in re.findall(r'<si>(.*?)</si>',x('xl/sharedStrings.xml'),re.S)] if 'xl/sharedStrings.xml' in z.namelist() else []
        rows=[];aba='xl/worksheets/sheet1.xml'
        try:# 1ª aba na ordem do arquivo, não necessariamente sheet1.xml
            rid=re.search(r'<sheet\b[^>]*?\sr:id="([^"]+)"',x('xl/workbook.xml'))[1]
            rel=re.search(r'<Relationship\b[^>]*\bId="'+re.escape(rid)+r'"[^>]*>',x('xl/_rels/workbook.xml.rels'))[0]
            alvo=re.search(r'Target="([^"]+)"',rel)[1];aba=alvo.lstrip('/') if alvo.startswith('/') else 'xl/'+alvo
        except (KeyError,TypeError):pass
        for r in re.findall(r'<row[^>]*>(.*?)</row>',x(aba),re.S):
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
        rows=list(csv.reader(io.StringIO(s),delimiter=';' if s.count(';')>s.count(',') else ','))# arquivo todo: a 1ª linha pode ser título
    def mapa(r):# coluna canônica -> índice, aceitando variações do nome da coluna
        m={}
        for i,h in enumerate(r):
            k=re.sub(r'[^a-z0-9]','',norm(h))
            for c,alias in COLUNAS.items():
                if k in alias and c not in m:m[c]=i
        return m
    cab=max(range(min(10,len(rows))),key=lambda i:len(mapa(rows[i])),default=0)# cabeçalho pode vir depois de linhas de título
    m=mapa(rows[cab]) if rows else {}
    falta=[n for c,n in (('conta_xp','conta'),('telefone','telefone'),('nome','nome')) if c not in m]
    if falta:sys.exit('nao achei na planilha a coluna de '+', '.join(falta)+'. A planilha precisa de uma coluna para conta, telefone e nome (apelido e opcional).')
    return [{c:(r[m[c]] if c in m and m[c]<len(r) else '').strip() for c in COLUNAS} for r in rows[cab+1:] if any(x.strip() for x in r)]
def tel_br(s):
    """Telefone em +55DDDNUMERO, ou (None, motivo). Mesma regra de normalizar_telefone em cliente.py."""
    d=re.sub(r'\D','',s or '')
    if not d:return None,'sem telefone'
    if d.startswith('00'):d=d[2:]
    elif d.startswith('0'):d=d[1:]
    if d.startswith('550') and len(d) in (13,14):d='55'+d[3:]
    if d.startswith('55') and len(d) in (12,13):nac=d[2:]
    elif len(d) in (10,11):nac=d
    else:return None,f'telefone inválido "{s}": informe DDD + número'
    ddd,num=nac[:2],nac[2:]
    if int(ddd) not in DDD:return None,f'telefone inválido "{s}": DDD {ddd} não existe'
    if len(num)==9 and num[0]!='9':return None,f'telefone inválido "{s}": celular deve começar com 9'
    if len(num)==8 and num[0] not in '2345':return None,f'telefone inválido "{s}": não é fixo nem celular'
    return '+55'+ddd+num,None
def ler_discurso(disc):
    """(texto, (mês, ano) da linha 'referência: MM/AAAA' ou None)."""
    t=Path(disc).read_text(encoding='utf-8-sig')
    r=re.search(r'refer\w+ncia:\s*(\d{1,2})/(\d{4})',t,re.I)
    linhas=[l.rstrip() for l in t.splitlines() if not l.lstrip().startswith(('#','<!--'))]
    return re.sub(r'\n{3,}','\n\n','\n'.join(linhas)).strip(),(r and (int(r[1]),r[2]))
def codigo(out):
    """Impressão digital do conteúdo do lote: muda se qualquer pacote ou o conferir-envios.csv mudar."""
    h=hashlib.sha256()
    for p in sorted(out.rglob('*')):
        if p.is_file() and p.name!='aprovacao.json':h.update(p.relative_to(out).as_posix().encode());h.update(p.read_bytes())
    return h.hexdigest()[:8]
def ler_lote(ref):
    out=BASE/f'lote-{ref}'
    if not (out/'conferir-envios.csv').is_file():sys.exit(f'lote {ref} nao existe: prepare o envio antes')
    with open(out/'conferir-envios.csv',encoding='utf-8',newline='') as fh:rows=list(csv.reader(fh))
    return out,rows
def aprovar(ref,cod,*revisar):
    out,rows=ler_lote(ref);lote={r[0]:r for r in rows[1:] if r}
    if cod!=codigo(out):sys.exit(f'o lote {ref} mudou depois do resumo (codigo {cod}, atual {codigo(out)}): mostre o resumo novo e peca nova aprovacao')
    ruins=[c for c in revisar if c not in lote or lote[c][4]!='revisar']
    if ruins:sys.exit('contas que nao estao como revisar neste lote: '+', '.join(ruins))
    (out/'aprovacao.json').write_text(json.dumps({'codigo':cod,'revisar':list(revisar),'aprovado_em':f'{datetime.now():%Y-%m-%d %H:%M}'}),encoding='utf-8')
    print(f'APROVADO lote {ref} | codigo {cod} | revisar incluidos: {len(revisar)}')
def historico():
    """Caminho do historico-envios.csv; renomeia o envios.csv de versões anteriores para não perder quem já recebeu."""
    p,velho=BASE/'historico-envios.csv',BASE/'envios.csv'
    if not p.exists() and velho.is_file():velho.rename(p)
    return p
def ler_envios():
    p=historico()
    if not p.is_file():return []
    with open(p,encoding='utf-8',newline='') as fh:return list(csv.reader(fh))
def checar(ref=None):
    """Confere historico-envios.csv (e, com REF, conferir-envios.csv e aprovação). Com REF e tudo certo, imprime a fila de envio."""
    err,avisos=[],[];env=ler_envios();ja={}
    if env and env[0]!=CAB_ENVIOS:err.append('historico-envios.csv: cabecalho diferente de '+','.join(CAB_ENVIOS))
    for i,r in enumerate(env[1:],2):
        if len(r)!=6:err.append(f'historico-envios.csv linha {i}: {len(r)} colunas em vez de 6');continue
        if not re.fullmatch(r'\d{4}-\d\d-\d\d',r[0]):err.append(f'historico-envios.csv linha {i}: data "{r[0]}" fora do formato AAAA-MM-DD')
        if not re.fullmatch(r'\d\d:\d\d',r[5]):err.append(f'historico-envios.csv linha {i}: horario "{r[5]}" fora do formato HH:MM')
        if not re.fullmatch(STATUS_ENVIO,r[4]):err.append(f'historico-envios.csv linha {i}: status "{r[4]}" desconhecido')
        elif not r[4].startswith('teste'):ja.setdefault((r[1],r[2]),[]).append(r[4])
    for (rf,c),st in ja.items():
        if st.count('enviado')>1:avisos.append(f'conta {c} tem {st.count("enviado")} envios registrados no lote {rf}')
    fila=[]
    if ref:
        out,rows=ler_lote(ref)
        if rows[0]!=CAB_LOTE:err.append('conferir-envios.csv: cabecalho diferente de '+','.join(CAB_LOTE))
        for r in rows[1:]:
            if len(r)!=len(CAB_LOTE) or r[4] not in ('pronto','revisar','bloqueado'):err.append(f'conferir-envios.csv: linha invalida {r}');continue
            if r[4]!='bloqueado' and not all((out/r[0]/f).is_file() for f in ('relatorio.pdf','mensagem.txt')):err.append(f'conta {r[0]}: pacote incompleto (falta PDF ou mensagem)')
        ap=out/'aprovacao.json'
        if not ap.is_file():err.append(f'lote {ref} sem aprovacao registrada (rode aprovar depois do sim do assessor)')
        else:
            ap=json.loads(ap.read_text(encoding='utf-8'))
            if ap['codigo']!=codigo(out):err.append(f'lote {ref} mudou depois da aprovacao: prepare o resumo de novo e peca nova aprovacao')
        if not err:
            for r in rows[1:]:
                feito=ja.get((ref,r[0]))
                if feito:fila.append(f'JA_REGISTRADO {r[0]} | {feito[-1]}')
                elif r[4]=='pronto' or (r[4]=='revisar' and r[0] in ap['revisar']):fila.append(f'ENVIAR {r[0]} | {r[1]} | {r[3]}')
                else:fila.append(f'PULAR {r[0]} | '+(r[5] if r[4]=='bloqueado' else 'revisar nao aprovado: '+r[5]))
    for a in avisos:print('AVISO: '+a)
    if err:
        for e in err:print('ERRO: '+e)
        sys.exit(1)
    print('OK'+(f' lote {ref}' if ref else ''))
    if fila:print('\n'.join(fila))
def sair(msg):
    print(msg)
    sys.exit(1)
def paragrafos(t):
    """Parágrafos reais: quebra de linha, sem linha em branco, pontas cortadas. CRLF e NBSP normalizados."""
    t=(t or '').replace('\r\n','\n').replace('\r','\n').replace('\xa0',' ')
    return [l.strip() for l in t.split('\n') if l.strip()]
def resolver_txt(ref,conta=None):
    """Caminho do .txt. Um argumento é o arquivo; dois são REF e CONTA do lote."""
    if conta is None:
        p=Path(ref)
        if not p.is_file():sair('falhou: arquivo não encontrado')
        return p
    out,rows=ler_lote(ref)
    if str(conta) not in {r[0] for r in rows[1:] if r}:sair(f'conta {conta} nao esta no lote {ref}')
    p=out/str(conta)/'mensagem.txt'
    if not p.is_file():sair('falhou: arquivo não encontrado')
    return p
def ler_txt(ref,conta=None):
    t=resolver_txt(ref,conta).read_text(encoding='utf-8')
    if not paragrafos(t):sair('vazio')
    return t
def garantir_xclip():
    if shutil.which('xclip'):return
    try:
        subprocess.run(['sudo','-n','env','DEBIAN_FRONTEND=noninteractive','apt-get','install','-y','xclip'],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        pass
    if not shutil.which('xclip'):sair('falhou: xclip ausente e a instalacao silenciosa falhou')
def xclip_gravar(texto):
    if not os.environ.get('DISPLAY'):sair('falhou: DISPLAY ausente; precisa ser o display do desktop do bot')
    garantir_xclip()
    # o xclip fica em segundo plano servindo o clipboard; com o stdout herdado ele prende o Shell que espera a saida fechar
    r=subprocess.run(['xclip','-selection','clipboard'],input=texto.encode('utf-8'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    if r.returncode!=0:sair('falhou: xclip nao gravou a area de transferencia')
def xclip_ler():
    if not os.environ.get('DISPLAY'):sair('falhou: DISPLAY ausente; precisa ser o display do desktop do bot')
    garantir_xclip()
    r=subprocess.run(['xclip','-o','-selection','clipboard'],capture_output=True)
    if r.returncode!=0:sair('falhou: xclip nao leu a area de transferencia')
    try:return r.stdout.decode('utf-8')
    except UnicodeDecodeError:sair('falhou: xclip nao leu a area de transferencia')
MARCA='[assessor: aguardando Ctrl+C da caixa]'
ESTADO_CLIP=BASE/'clipboard-estado'
def estado_clip(v=None):
    """Passo da trava de texto em que o clipboard está: copiado, marcado ou vazio. Sem argumento, lê."""
    if v is None:return ESTADO_CLIP.read_text(encoding='utf-8') if ESTADO_CLIP.is_file() else ''
    ESTADO_CLIP.parent.mkdir(parents=True,exist_ok=True);ESTADO_CLIP.write_text(v,encoding='utf-8')
def diff_paragrafos(esperado,obtido):
    a,b=paragrafos(esperado),paragrafos(obtido)
    if a==b:return None
    mot,n=[],min(len(a),len(b))
    for i in range(n):
        if a[i]!=b[i]:mot.append(f'parágrafo {i+1} diferente');break
    if len(b)<len(a):mot.append(f'{len(a)-len(b)} faltando')
    elif len(b)>len(a):mot.append(f'{len(b)-len(a)} sobrando')
    return 'nao bate: '+', '.join(mot)
def copiar(ref,conta=None):
    """Põe o conteúdo exato do .txt na área de transferência."""
    xclip_gravar(ler_txt(ref,conta));estado_clip('copiado')
    print('copiado')
def marcar():
    """Troca o clipboard pela marca, depois do Ctrl+V. Sem isso, um Ctrl+C que não aconteceu deixaria no clipboard o texto do copiar e a conferência bateria sem ler a caixa."""
    xclip_gravar(MARCA);estado_clip('marcado')
    print('marcado')
def conferir_caixa(ref,conta=None):
    """Compara o clipboard (Ctrl+A Ctrl+C na caixa, depois de marcar) com o .txt, por parágrafos reais. Vale uma vez por marcar."""
    t=ler_txt(ref,conta)
    if estado_clip()!='marcado':sair('falhou: rode marcar depois do Ctrl+V e antes do Ctrl+A e Ctrl+C')
    estado_clip('')
    c=xclip_ler()
    if c.strip()==MARCA:sair('nao bate: o clipboard ainda tem a marca; o Ctrl+A e Ctrl+C da caixa nao aconteceu')
    mot=diff_paragrafos(t,c)
    if mot:sair(mot)
    print('bate')
def registrar(ref,conta,status,horario=None):
    """Acrescenta uma linha a historico-envios.csv (o csv cuida de vírgulas e aspas no motivo)."""
    if not re.fullmatch(STATUS_ENVIO,status):sys.exit(f'status "{status}" invalido: use enviado, falhou: <motivo>, pulado: <motivo> ou teste: <resultado>')
    horario=horario or f'{datetime.now():%H:%M}'
    if not re.fullmatch(r'\d\d:\d\d',horario):sys.exit(f'horario "{horario}" invalido: use HH:MM')
    _,rows=ler_lote(ref);lote={r[0]:r for r in rows[1:] if r}
    if conta not in lote:sys.exit(f'conta {conta} nao esta no lote {ref}')
    p=historico();novo=not p.is_file()
    with open(p,'a',encoding='utf-8',newline='') as fh:
        w=csv.writer(fh)
        if novo:w.writerow(CAB_ENVIOS)
        w.writerow([f'{datetime.now():%Y-%m-%d}',ref,conta,lote[conta][2],status,horario])
    print(f'REGISTRADO {conta} | {status}')
def importar(planilha):
    """Limpa a planilha do assessor e grava a ativa: BASE/clientes.csv com as 4 colunas canônicas.

    Conta só com dígitos, telefone em +55 quando válido (inválido fica como veio, para o lote bloquear),
    espaços colapsados. A planilha ativa anterior vira clientes.bak-AAAAMMDD-HHMM.<ext>.
    """
    linhas=ler_planilha(planilha);limpas,sem_conta,invalidos=[],0,[]
    for l in linhas:
        c=re.sub(r'\D','',l['conta_xp'])
        if not c:sem_conta+=1;continue
        tel,erro=tel_br(l['telefone'])
        if erro:invalidos.append(f'{c} ({erro})')
        limpas.append([c,tel or l['telefone'],' '.join(l['nome'].split()),' '.join(l['apelido'].split())])
    if not limpas:sys.exit('a planilha nao tem nenhuma linha com conta: confira se e a planilha de clientes')
    BASE.mkdir(parents=True,exist_ok=True);ativa=BASE/'clientes.csv'
    for p in (ativa,BASE/'clientes.xlsx'):# já lida em memória: pode ser a própria planilha importada
        if p.is_file():
            bak=BASE/f'clientes.bak-{datetime.now():%Y%m%d-%H%M}{p.suffix}'
            p.rename(bak if not bak.exists() else bak.with_name(f'clientes.bak-{datetime.now():%Y%m%d-%H%M%S}{p.suffix}'))
    with open(ativa,'w',encoding='utf-8',newline='') as fh:
        w=csv.writer(fh);w.writerow(list(COLUNAS));w.writerows(limpas)
    rep=[c for c,n in Counter(r[0] for r in limpas).items() if n>1]
    print(f'IMPORTADO {len(limpas)} clientes -> {ativa}')
    if sem_conta:print(f'AVISO: {sem_conta} linhas sem conta ignoradas')
    if invalidos:print(f'AVISO: {len(invalidos)} telefones invalidos (vao bloquear no lote): '+'; '.join(invalidos))
    if rep:print('AVISO: contas repetidas (vao bloquear no lote): '+', '.join(rep))
    sem=sum(1 for r in limpas if not r[3])
    if sem:print(f'AVISO: {sem} sem apelido (o lote usa o 1o nome)')
def main(zp,planilha,disc):
    discurso,mref=ler_discurso(disc)
    if not discurso:sys.exit('discurso macro vazio')
    if len(discurso)>TETO_DISCURSO:sys.exit(f'discurso macro com {len(discurso)} caracteres: o teto e {TETO_DISCURSO}. Encurte o discurso antes de preparar')
    tmp=BASE/'_pdfs';shutil.rmtree(tmp,ignore_errors=True)
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
    if not datas:sys.exit('nenhum PDF do relatório mensal de performance da corretora legível no zip')
    a,me,di=datas.most_common(1)[0][0];ref=f'{a}-{me}-{di}';out=BASE/f'lote-{ref}'
    if mref!=(int(me),a):
        shutil.rmtree(tmp,ignore_errors=True)
        sys.exit(f'discurso do mes {mref[0]:02d}/{mref[1]} e lote do mes {me}/{a}: publique o discurso do mes antes de preparar' if mref else 'discurso sem a linha "referencia: MM/AAAA": nao da para saber o mes dele')
    shutil.rmtree(out,ignore_errors=True);out.mkdir(parents=True)
    linhas=ler_planilha(planilha);cont=Counter(re.sub(r'\D','',l['conta_xp']) for l in linhas);res=[]
    for l in linhas:
        c=re.sub(r'\D','',l['conta_xp']);bloq,rev,aviso=[],[],''
        if cont[c]>1:bloq.append('conta repetida na planilha')
        tel,erro=tel_br(l['telefone'])
        if erro:bloq.append(erro)
        ap=l['apelido']
        if not ap:
            ap=(l['nome'].split() or [''])[0];ap=ap.capitalize() if ap.isupper() else ap
            aviso=f'sem apelido, usado "{ap}"'
        if c not in pdfs:bloq.append('sem PDF no lote')
        else:
            d,f,err=pdfs.pop(c)
            if err:bloq.append('não lido: '+', '.join(err))
            if f.get('data',(a,me,di))!=(a,me,di):bloq.append('data de referência diferente do lote')
            if c in dup:rev.append('conta repetida no zip')
            nn=norm(l['nome']).split()
            if nomes[c] and (not nn or norm(nomes[c]).split()[0]!=nn[0]):rev.append(f'nome no PDF "{nomes[c]}" ≠ planilha "{l["nome"]}"')
            if not err:
                msg=MODELO.format(apelido=ap,mes_ano=f'{MESES[int(me)-1]}/{a}',discurso_macro=discurso,janelas=janelas(f),**f)
                if tam(msg)>LIMITE_MSG:bloq.append(f'mensagem com {tam(msg)} caracteres, acima do limite de {LIMITE_MSG}')
                p=out/c;p.mkdir();shutil.copy(d,p/'relatorio.pdf');(p/'mensagem.txt').write_text(msg,encoding='utf-8')
        res.append([c,l['nome'],ap,tel or l['telefone'],'bloqueado' if bloq else 'revisar' if rev else 'pronto','; '.join(bloq+rev),aviso])
    for c,(d,f,err) in pdfs.items():res.append([c,nomes[c],'','','bloqueado','PDF sem linha na planilha',''])
    with open(out/'conferir-envios.csv','w',newline='',encoding='utf-8') as fh:
        w=csv.writer(fh);w.writerow(CAB_LOTE);w.writerows(res)
    shutil.rmtree(tmp,ignore_errors=True)
    print(f'LOTE {ref} -> {out}');print(dict(Counter(r[4] for r in res)))
    for r in res:
        if r[5]:print(f'{r[0]} {r[1]}: {r[4]} - {r[5]}')
    sem=[r for r in res if r[6]]
    if sem:print(f'AVISO: {len(sem)} sem apelido, usado o primeiro nome: '+'; '.join(f'{r[0]} {r[2]}' for r in sem))
    print(f'CODIGO {codigo(out)}')
if __name__=='__main__':
    cmd={'importar':importar,'aprovar':aprovar,'checar':checar,'registrar':registrar,'copiar':copiar,'marcar':marcar,'conferir-caixa':conferir_caixa}
    if len(sys.argv)>1 and sys.argv[1] in cmd:cmd[sys.argv[1]](*sys.argv[2:])
    elif len(sys.argv)>1 and not sys.argv[1].lower().endswith('.zip'):sys.exit(f'subcomando desconhecido: {sys.argv[1]} (use '+', '.join(cmd)+' ou LOTE.zip)')
    else:main(*sys.argv[1:4])

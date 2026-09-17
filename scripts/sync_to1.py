#!/usr/bin/env python3
"""Read only the public report tab; fail closed on changed schema or invalid totals."""
import csv, io, json, re, hashlib, sys, urllib.request
from pathlib import Path
from decimal import Decimal
ROOT=Path(__file__).resolve().parents[1]
URL='https://docs.google.com/spreadsheets/d/1QADezkYsPR61Uh5CD8RSVFlLymvN8N5udZAI4BukJiA/edit?gid=1905427817#gid=1905427817'
CSV=URL.split('/edit')[0]+'/export?format=csv&gid=1905427817'
PAT=r'(<script type="application/json" id="data">)(.*?)(</script>)'
def number(s):
    s=s.strip()
    if s in ('','—','-'): return None
    if not re.fullmatch(r'\d{1,3}(?:\.\d{3})*(?:,\d+)?|\d+(?:,\d+)?',s): raise ValueError('Invalid numeric cell: '+s)
    return Decimal(s.replace('.','').replace(',','.'))
def build(raw):
    rows=list(csv.reader(io.StringIO(raw.decode('utf-8-sig'))))
    assert len(rows)>=8 and 'TỔ CÔNG TÁC SỐ 1' in rows[0][0]
    assert len(rows[4])==12 and rows[4][1].strip()=='DỰ ÁN' and '2026' in rows[4][3] and 'triệu đồng' in rows[4][3]
    assert 'lũy kế' in rows[4][4] and 'Tóm tắt tiến độ'==rows[4][10]
    assert 'tháng 9' in rows[5][7] and 'tháng 9' in rows[5][8]
    html=(ROOT/'index.html').read_text(); data=json.loads(re.search(PAT,html,re.S)[2]); group=data['groups'][0]['name']
    other=[p for p in data['projects'] if p['group']!=group]
    headers=[rows[5][i] if i in (7,8,9) else rows[4][i] for i in range(12)]
    projects=[]; totals_row=None
    for ix,r in enumerate(rows[6:],7):
        r=(r+['']*12)[:12]
        if not any(r): continue
        if not r[0].strip() and not r[1].strip() and r[2].strip():
            assert totals_row is None; totals_row=r; continue
        assert totals_row is None and r[0].strip().isdigit() and r[1].strip(), 'Unexpected report row'
        stt=int(r[0]); assert stt==len(projects)+1
        vals=[number(r[i]) for i in (2,3,4,5,7,8)]
        assert all(v is None or v>=0 for v in vals)
        inv,plan,paid,left,monthly,monthlyplan=[None if v is None else float(v/1000) for v in vals]
        rate=number(r[6].strip().removesuffix('%')); rate=None if rate is None else float(rate)
        p=dict(id=100000+stt,stt=stt,sheet='Báo cáo',row=ix,group=group,name=r[1],investment=inv,plan=plan,paid=paid,left=left,base=plan,rate=rate,owner='Ban Quản lý các Khu kinh tế và khu công nghiệp tỉnh',difficulty=r[11],progress=r[10],note=None,raw=r,sourceHeaders=headers,sourceFile='Theo dõi giải ngân Tổ công tác số 1',sourceUrl=URL,leaderOrigin='Tổ 1 · PCT Thường trực Hồ Thị Nguyên Thảo (phân công theo yêu cầu)',rateOrigin='Tỷ lệ ghi trong nguồn',baseOrigin='KH vốn 2026, triệu đồng quy đổi sang tỷ đồng (chia 1.000)',quality=[],status='blank' if not r[11].strip() else ('no' if r[11].strip().lower() in ('không','không có') else 'yes'),monthlyPaid=monthly,monthlyPlan=monthlyplan,monthlyRate=r[9],appendices=[],sources=[],pdfSources=[])
        p.update({k:None for k in ['carry','current','paidCarry','paidCurrent','leftCarry','leftCurrent']})
        projects.append(p)
    assert projects and totals_row is not None
    for col,key in [(2,'investment'),(3,'plan'),(4,'paid'),(5,'left'),(7,'monthlyPaid'),(8,'monthlyPlan')]:
        total=number(totals_row[col]); values=[p[key] for p in projects]
        if total is not None: assert abs(sum(Decimal(str(v)) for v in values if v is not None)-total/1000)<Decimal('0.000001'), 'Source total differs: '+key
    data['projects']=projects+other; data['groups'][0]['expected']=len(projects)
    data['to1Source']=dict(url=URL,date=rows[0][11],sha256=hashlib.sha256(raw).hexdigest(),headers=headers,totals=totals_row)
    def audit(pp):
        return dict(count=len(pp),sums={k:str(sum(Decimal(str(p[k])) for p in pp if p[k] is not None)) for k in ['investment','plan','paid','left']},missing={k:sum(p[k] is None for p in pp) for k in ['investment','plan','paid','rate']},difficulty=sum(p['status']=='yes' for p in pp))
    data['audit']['groups'][group]=audit(projects);data['audit']['all']=audit(data['projects'])
    # Remove superseded source notes for Tổ 1 and whole-catalogue totals.
    data['sourceNotes']=[r for r in data.get('sourceNotes',[]) if not r or r[0] not in ('Tổ 1','TỔNG CỘNG')]
    def embed(d): return re.sub(PAT,lambda m:m[1]+json.dumps(d,ensure_ascii=False).replace('<','\\u003c')+m[3],html,flags=re.S)
    combined=embed(data)
    single=json.loads(json.dumps(data));single['projects']=projects;single['groups']=data['groups'][:1];single['audit']={'all':audit(projects),'groups':{group:audit(projects)}};single['sourceNotes']=[];single['view']='to-1'
    separate=embed(single).replace('<title>Dashboard theo dõi danh mục các dự án</title>','<title>Dashboard Tổ 1 – Hồ Thị Nguyên Thảo</title>')
    assert [p for p in json.loads(re.search(PAT,combined,re.S)[2])['projects'] if p['group']!=group]==other
    (ROOT/'index.html').write_text(combined);(ROOT/'to-1/index.html').write_text(separate)
    print('Validated and synchronized',len(projects),'Tổ 1 projects;',len(other),'other projects unchanged')
if __name__=='__main__':
    raw=Path(sys.argv[1]).read_bytes() if len(sys.argv)>1 else urllib.request.urlopen(CSV,timeout=60).read(2_000_000)
    build(raw)

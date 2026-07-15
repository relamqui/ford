import re

with open('relatorio.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace header and tab texts
html = html.replace('NPS de satisfação e eficiência de tempo de atendimento', 'Motivos de Finalização e Eficiência de tempo de atendimento')
html = html.replace('⭐ NPS de Satisfação', '📋 Motivos de Finalização')

# Replace API endpoint strings in JS
html = html.replace('/api/reports/nps-filiais', '/api/reports/motivos-filiais')
html = html.replace('/api/reports/nps-atendentes', '/api/reports/motivos-atendentes')

# Replace loadNpsF body
nps_f_pattern = re.compile(r'/\* ══ NPS FILIAIS ══ \*/\s*async function loadNpsF\(\) \{.*?\}(?=\s*/\* ══ NPS ATENDENTES ══ \*/)', re.DOTALL)
motivos_f_code = '''/* ══ MOTIVOS FILIAIS ══ */
  async function loadNpsF() {
    const el = document.getElementById('nps-filiais-box');
    el.innerHTML = '<div class="spinner nps-spin"></div>';
    try {
      const r = await fetch(API+'/api/reports/motivos-filiais'+qp(), {headers:{Authorization:'Bearer '+tok()}});
      const j = await r.json();
      if(!r.ok||!j.success){el.innerHTML=errH(j.error||'Erro');return;}
      const d = j.data||[];
      if(!d.length){el.innerHTML=empH('Nenhum dado encontrado.');return;}
      el.innerHTML = d.map((f,fi)=>{
        let tvendas=0,torc=0,tout=0,ttot=0;
        f.setores.forEach(s=>{tvendas+=s.vendas;torc+=s.orcamentos;tout+=s.outros;ttot+=s.total;});
        const setoresHtml = f.setores.map(s=>{
          return '<div class="setor-card"><div class="setor-card-header"><div><div class="setor-name">'+s.setor+'</div><div class="setor-meta">'+s.total+' atendimento(s)</div></div></div>'
            +'<div class="nps-bars" style="margin-top:10px">'
            +'<div class="nps-bar-row"><span class="nps-bar-label">💰 Vendas</span><div class="nps-bar-track"><div class="nps-bar-fill prom" style="width:'+bp(s.vendas,s.total)+'%"></div></div><span class="nps-bar-count">'+s.vendas+'</span></div>'
            +'<div class="nps-bar-row"><span class="nps-bar-label">📝 Orç.</span><div class="nps-bar-track"><div class="nps-bar-fill neut" style="width:'+bp(s.orcamentos,s.total)+'%"></div></div><span class="nps-bar-count">'+s.orcamentos+'</span></div>'
            +'<div class="nps-bar-row"><span class="nps-bar-label">❓ Outros</span><div class="nps-bar-track"><div class="nps-bar-fill detr" style="width:'+bp(s.outros,s.total)+'%"></div></div><span class="nps-bar-count">'+s.outros+'</span></div>'
            +'</div></div>';
        }).join('');
        return '<div class="filial-block" id="nf'+fi+'">'
          +'<div class="filial-header" onclick="tog(\'nf'+fi+'\')">'
          +'<div class="filial-header-left"><div class="filial-icon ni">🏢</div><div><div class="filial-name">'+f.filial+'</div><div class="filial-meta">'+f.setores.length+' setor(es) · '+ttot+' atendimentos</div></div></div>'
          +'<div class="filial-header-right"><div class="stat-inline"><div class="stat-val media-nota alta">💰 '+tvendas+'</div><div class="stat-lbl">Vendas</div></div>'
          +'<div class="stat-inline"><div class="stat-val media-nota media">📝 '+torc+'</div><div class="stat-lbl">Orçamentos</div></div>'
          +'<div class="stat-inline"><div class="stat-val media-nota baixa">❓ '+tout+'</div><div class="stat-lbl">Outros</div></div>'
          +chv()+'</div></div>'
          +'<div class="filial-body"><div class="setores-grid">'+setoresHtml+'</div></div></div>';
      }).join('');
    } catch(e){el.innerHTML=errH('Erro de conexão.');}
  }'''
html = nps_f_pattern.sub(motivos_f_code, html)

# Replace loadNpsA body
nps_a_pattern = re.compile(r'/\* ══ NPS ATENDENTES ══ \*/\s*async function loadNpsA\(\) \{.*?\}(?=\s*/\* ══ TEMPO FILIAIS ══ \*/)', re.DOTALL)
motivos_a_code = '''/* ══ MOTIVOS ATENDENTES ══ */
  async function loadNpsA() {
    const el = document.getElementById('nps-atendentes-box');
    el.innerHTML = '<div class="spinner nps-spin"></div>';
    try {
      const r = await fetch(API+'/api/reports/motivos-atendentes'+qp(), {headers:{Authorization:'Bearer '+tok()}});
      const j = await r.json();
      if(!r.ok||!j.success){el.innerHTML=errH(j.error||'Erro');return;}
      const d = j.data||[];
      if(!d.length){el.innerHTML=empH('Nenhum dado encontrado.');return;}
      el.innerHTML='<div class="ranking-table-wrap"><table class="rtable"><thead><tr>'
        +'<th>Posição</th><th>Atendente</th><th>Filial</th><th>Vendas</th><th>Orçamentos</th><th>Outros</th><th>Total Atendimentos</th>'
        +'</tr></thead><tbody>'+d.map((r,i)=>'<tr>'
          +'<td><div class="rank-pos"><span class="medal">'+(medals[i]||'')+'</span><span>#'+(i+1)+'</span></div></td>'
          +'<td><div class="att-info"><span class="att-name">'+r.atendente+'</span><span class="att-sub">'+r.setor+'</span></div></td>'
          +'<td style="color:var(--text-secondary)">'+r.filial+'</td>'
          +'<td><span class="pill prom" style="font-size:14px;font-weight:bold">💰 '+r.vendas+'</span></td>'
          +'<td><span class="pill neut">📝 '+r.orcamentos+'</span></td>'
          +'<td><span class="pill detr">❓ '+r.outros+'</span></td>'
          +'<td style="font-weight:700">'+r.total+'</td></tr>').join('')
        +'</tbody></table></div>';
    } catch(e){el.innerHTML=errH('Erro de conexão.');}
  }'''
html = nps_a_pattern.sub(motivos_a_code, html)

with open('relatorio.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('relatorio.html updated')

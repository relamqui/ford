import re

with open('app.py', 'r', encoding='utf-8') as f:
    app_code = f.read()

nps_filiais_pattern = re.compile(r'@app\.route\(\'/api/reports/nps-filiais\', methods=\[\'GET\'\]\).*?return jsonify\(\{\'success\': True, \'data\': list\(filiais\.values\(\)\)\}\)', re.DOTALL)

motivos_filiais_code = '''@app.route('/api/reports/motivos-filiais', methods=['GET'])
@auth_required
@admin_or_gestor_required
def report_motivos_filiais():
    """Retorna agrupamento de motivos por Filial e Setor."""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        filters = ""
        params = {}
        if start_date:
            filters += " AND (m.criado_em IS NULL OR m.criado_em >= :start_date)"
            params['start_date'] = start_date
        if end_date:
            filters += " AND (m.criado_em IS NULL OR m.criado_em <= :end_date)"
            params['end_date'] = end_date + ' 23:59:59'

        sql = db_sql.text(f"""
            SELECT COALESCE(u.filial, 'Sem Filial') as filial, 
                   COALESCE(u.setor, 'Sem Setor') as setor, 
                   m.motivo, 
                   COUNT(*) as qtd
            FROM motivo_finalizacao m
            LEFT JOIN user u ON u.name = m.atendente
            WHERE 1=1 {filters}
            GROUP BY u.filial, u.setor, m.motivo
            ORDER BY u.filial, u.setor, m.motivo
        """)
        rows = db_sql.session.execute(sql, params).fetchall()

        filiais = {}
        for row in rows:
            filial = row[0]
            setor = row[1]
            motivo = row[2]
            qtd = row[3]

            if filial not in filiais:
                filiais[filial] = {'filial': filial, 'setores': {}}
            
            if setor not in filiais[filial]['setores']:
                filiais[filial]['setores'][setor] = {
                    'setor': setor,
                    'vendas': 0,
                    'orcamentos': 0,
                    'outros': 0,
                    'total': 0
                }
            
            s = filiais[filial]['setores'][setor]
            s['total'] += qtd
            if motivo == 'Venda':
                s['vendas'] += qtd
            elif motivo == 'Orçamento':
                s['orcamentos'] += qtd
            else:
                s['outros'] += qtd

        result = []
        for f_name, f_data in filiais.items():
            f_data['setores'] = list(f_data['setores'].values())
            result.append(f_data)

        return jsonify({'success': True, 'data': result})'''

app_code = nps_filiais_pattern.sub(motivos_filiais_code, app_code)

nps_atendentes_pattern = re.compile(r'@app\.route\(\'/api/reports/nps-atendentes\', methods=\[\'GET\'\]\).*?return jsonify\(\{\'success\': True, \'data\': result\}\)', re.DOTALL)

motivos_atendentes_code = '''@app.route('/api/reports/motivos-atendentes', methods=['GET'])
@auth_required
@admin_or_gestor_required
def report_motivos_atendentes():
    """Retorna agrupamento de motivos por Atendente."""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        filters = ""
        params = {}
        if start_date:
            filters += " AND (m.criado_em IS NULL OR m.criado_em >= :start_date)"
            params['start_date'] = start_date
        if end_date:
            filters += " AND (m.criado_em IS NULL OR m.criado_em <= :end_date)"
            params['end_date'] = end_date + ' 23:59:59'

        sql = db_sql.text(f"""
            SELECT COALESCE(m.atendente, 'Sem Atendente') as atendente, 
                   COALESCE(u.filial, 'Sem Filial') as filial, 
                   COALESCE(u.setor, 'Sem Setor') as setor, 
                   m.motivo, 
                   COUNT(*) as qtd
            FROM motivo_finalizacao m
            LEFT JOIN user u ON u.name = m.atendente
            WHERE 1=1 {filters}
            GROUP BY m.atendente, u.filial, u.setor, m.motivo
            ORDER BY m.atendente, m.motivo
        """)
        rows = db_sql.session.execute(sql, params).fetchall()

        atendentes = {}
        for row in rows:
            atendente = row[0]
            filial = row[1]
            setor = row[2]
            motivo = row[3]
            qtd = row[4]

            if atendente not in atendentes:
                atendentes[atendente] = {
                    'atendente': atendente,
                    'filial': filial,
                    'setor': setor,
                    'vendas': 0,
                    'orcamentos': 0,
                    'outros': 0,
                    'total': 0
                }
            
            a = atendentes[atendente]
            a['total'] += qtd
            if motivo == 'Venda':
                a['vendas'] += qtd
            elif motivo == 'Orçamento':
                a['orcamentos'] += qtd
            else:
                a['outros'] += qtd

        result = list(atendentes.values())
        result.sort(key=lambda x: x['total'], reverse=True)

        return jsonify({'success': True, 'data': result})'''

app_code = nps_atendentes_pattern.sub(motivos_atendentes_code, app_code)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_code)

print('app.py updated')

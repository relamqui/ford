from app import app, db_sql, NpsVoto
with app.app_context():
    print(app.config['SQLALCHEMY_DATABASE_URI'])
    votos = NpsVoto.query.filter_by(data_voto=None).all()
    for v in votos:
        v.data_voto = '2026-07-02T12:00:00'
    db_sql.session.commit()
    print(f'Updated {len(votos)} votes with NULL data_voto.')

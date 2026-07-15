from app import app, db_sql
from sqlalchemy import text

with app.app_context():
    try:
        db_sql.session.execute(text("ALTER TABLE atendimentos_chat DROP COLUMN ultimo_setor"))
        db_sql.session.commit()
        print("Dropped ultimo_setor from actual DB")
    except Exception as e:
        db_sql.session.rollback()
        print(f"Error dropping ultimo_setor: {e}")

    try:
        db_sql.session.execute(text("ALTER TABLE atendimentos_chat DROP COLUMN ultimo_atendente"))
        db_sql.session.commit()
        print("Dropped ultimo_atendente from actual DB")
    except Exception as e:
        db_sql.session.rollback()
        print(f"Error dropping ultimo_atendente: {e}")

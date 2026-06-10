from app import app, db_sql, DriverLocation

with app.app_context():
    db_sql.create_all()
    print("Tabelas criadas com sucesso (as que não existiam)!")

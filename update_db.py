import sqlite3
import os

DB_PATH = 'data/wpcrm.db'

def main():
    if not os.path.exists(DB_PATH):
        print(f"DB não encontrado em {DB_PATH}")
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Adicionar codigo_verificacao
    try:
        cursor.execute("ALTER TABLE entrega ADD COLUMN codigo_verificacao VARCHAR(20)")
        print("Coluna codigo_verificacao adicionada com sucesso.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Coluna codigo_verificacao já existe.")
        else:
            print(f"Erro ao adicionar codigo_verificacao: {e}")
            
    # Adicionar entregador_id
    try:
        cursor.execute("ALTER TABLE entrega ADD COLUMN entregador_id INTEGER")
        print("Coluna entregador_id adicionada com sucesso.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Coluna entregador_id já existe.")
        else:
            print(f"Erro ao adicionar entregador_id: {e}")
            
    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()

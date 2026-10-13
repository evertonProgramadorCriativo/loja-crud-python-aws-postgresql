from sqlalchemy import text

from app.database import engine

with engine.connect() as conn:
    print("Banco:", conn.execute(text("SELECT current_database()")).scalar())
    print("Versão:", conn.execute(text("SELECT version()")).scalar())
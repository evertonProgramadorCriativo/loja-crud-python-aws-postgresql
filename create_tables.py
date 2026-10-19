from sqlalchemy import inspect

from app.database import Base, engine
import app.models  # noqa: F401  (importar faz os models serem registrados)

Base.metadata.create_all(bind=engine)

inspector = inspect(engine)
print("Tabelas no banco:")
for table in inspector.get_table_names():
    colunas = [c["name"] for c in inspector.get_columns(table)]
    print(f"  - {table}: {', '.join(colunas)}")

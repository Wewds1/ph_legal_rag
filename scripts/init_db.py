from pathlib import Path
from sqlalchemy import text, create_engine
from engine.config import settings

def init_db():
    engine = create_engine(settings.database_url)
    schema_file = Path("database/schema.sql").read_text()
    
    with engine.connect() as conn:
        conn.execute(text(schema_file))
        conn.commit()
    
    print("Database schema created successfully")

if __name__ == "__main__":
    init_db()
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 프로젝트 루트 경로
DB_PATH = os.path.join(BASE_DIR, "data", "university.db")

def get_db_schema(db_path=DB_PATH):
    """
    Reads the schema of the SQLite database and returns a string description with sample data.
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    tables = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';").fetchall()
    schema = ""
    for (table_name,) in tables:
        schema += f"Table `{table_name}` columns: "
        columns = c.execute(f"PRAGMA table_info({table_name});").fetchall()
        schema += ", ".join([f"{col[1]} ({col[2]})" for col in columns]) + ".\n"

        # Fetch sample data
        sample_data = c.execute(f"SELECT * FROM {table_name} LIMIT 3").fetchall()
        if sample_data:
            schema += f"Sample data from {table_name}:\n"
            for row in sample_data:
                schema += f"  {row}\n"
            schema += "\n"
    conn.close()
    return schema

def query_university_db(sql_query: str):
    """
    Executes a SQL query on university.db and returns the result.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(sql_query)
        rows = c.fetchall()
        columns = [desc[0] for desc in c.description] if c.description else []
        conn.close()
        return {"columns": columns, "rows": rows}
    except Exception as e:
        return {"error": str(e)}
from pathlib import Path
import sqlite3
from Config.LimpiezaConfig import LimpiezaConfig


class LimpiezaLoader:
    """Clase para guardar DataFrames limpios en CSV o SQLite."""

    def __init__(self, df):
        self.df = df.copy()

    def to_csv(self, output_path: str, index: bool = False, encoding: str = 'utf-8'):
        """Guarda el DataFrame en CSV; crea la carpeta si es necesario."""
        try:
            p = Path(output_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            self.df.to_csv(p, index=index, encoding=encoding)
            print(f"Datos guardados en {p}")
        except Exception as e:
            print(f"Error al guardar datos en CSV: {e}")

    def to_sqlite(self, db_path: str = None, table_name: str = None, if_exists: str = 'replace'):
        """Guarda el DataFrame en una base de datos SQLite (crea carpeta si es necesario)."""
        db_path = db_path or str(LimpiezaConfig.SQLITE_DB_PATH)
        table_name = table_name or LimpiezaConfig.SQLITE_TABLE
        try:
            p = Path(db_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(p))
            try:
                self.df.to_sql(table_name, conn, if_exists=if_exists, index=False)
            finally:
                conn.close()
            print(f"Datos guardados en la base de datos SQLite: {p}, tabla: {table_name}")
        except Exception as e:
            print(f"Error al guardar en SQLite: {e}")
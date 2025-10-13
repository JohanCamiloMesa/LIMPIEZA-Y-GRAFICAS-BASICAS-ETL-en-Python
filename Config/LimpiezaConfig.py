from pathlib import Path

class LimpiezaConfig:
    """
    Clase de configuración para rutas y parámetros del ETL.
    """

    BASE_DIR = Path(__file__).parent.parent
    SQLITE_DB_PATH = BASE_DIR / 'Extract' / 'Files' / 'Limpieza.db'
    SQLITE_TABLE = 'Limpieza_data'
    # Rutas relativas basadas en el directorio base del proyecto
    INPUT_PATH = str(BASE_DIR / 'Extract' / 'Files' / 'stock_senti_analysis.csv')
    OUTPUT_PATH = str(BASE_DIR / 'Extract' / 'Files' / 'output_clean.csv')
    
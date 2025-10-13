# Importaciones de clases del proyecto
from Extract.LimpiezaExtract import LimpiezaExtract
from Transform.LimpiezaTransform import full_clean_stock_sentiment
from Config.LimpiezaConfig import LimpiezaConfig
from Load.LimpiezaLoader import LimpiezaLoader


def run_pipeline():
	# Extracción
	extractor = LimpiezaExtract(LimpiezaConfig.INPUT_PATH)
	extractor.queries()
	df = extractor.data

	print("\n--- DATASET ORIGINAL (primeras 5 filas) ---\n")
	print(df.head(5))

	# Transformación / limpieza completa
	print("\n--- INICIANDO LIMPIEZA ---\n")
	df_clean = full_clean_stock_sentiment(df)
	summary = df_clean.attrs.get('cleaning_summary', {})
	print('Resumen de limpieza:', summary)
	print('\n--- DATASET LIMPIO (primeras 5 filas) ---\n')
	print(df_clean.head(5))

	# Cargar / Guardar
	loader = LimpiezaLoader(df_clean)
	print(f"Guardando CSV limpio en: {LimpiezaConfig.OUTPUT_PATH}")
	loader.to_csv(LimpiezaConfig.OUTPUT_PATH)
	print(f"Guardando en SQLite: {LimpiezaConfig.SQLITE_DB_PATH} (tabla: {LimpiezaConfig.SQLITE_TABLE})")
	loader.to_sqlite(str(LimpiezaConfig.SQLITE_DB_PATH), LimpiezaConfig.SQLITE_TABLE)


if __name__ == '__main__':
	run_pipeline()

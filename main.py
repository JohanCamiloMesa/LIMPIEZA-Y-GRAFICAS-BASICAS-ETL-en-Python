# Importaciones de clases del proyecto
from Extract.ETLpremierExtract import SpotifyandYoutubeExtract
from Transform.ETLpremierClean import SpotifyandYoutubeClean
from Config.config import Config
from Load.loader import Loader
from Extract.Graphic.ETLpremierGraphic import (
	grafica_promedio_goles_liverpool,
	grafica_promedio_tarjetas_por_equipo,
	grafica_promedio_goles_por_equipo
)

# Extracción de datos
extractor = SpotifyandYoutubeExtract(Config.INPUT_PATH)
extractor.queries()
df = extractor.data

# Mostrar el dataset original completo antes de la limpieza
print("\n--- DATASET ORIGINAL ---\n")
print(df)

# Limpieza de datos

# Limpieza de datos
limpieza = SpotifyandYoutubeClean(df)
resultados_nulos_ceros = limpieza.verificar_nulos_ceros()
print("\n--- NULOS Y CEROS POR COLUMNA ---\n")
print(resultados_nulos_ceros)

# Eliminar equipos específicos antes de limpiar columnas
equipos_a_eliminar = ['Brighton & Hove Albion', 'Ipswich Town']
df_sin_equipos = limpieza.eliminar_equipos(equipos_a_eliminar)

limpieza_final = SpotifyandYoutubeClean(df_sin_equipos)
df_limpio = limpieza_final.limpiar_columnas()
print("\n--- DATASET LIMPIO ---\n")
print(df_limpio)

# Guardar el DataFrame limpio en la ruta de salida configurada
loader = Loader(df_limpio)
loader.to_csv(Config.OUTPUT_PATH)

# Mostrar el DataFrame de nulos y ceros del dataset limpio
print("\n--- NULOS Y CEROS EN DATASET LIMPIO ---\n")
resultados_nulos_ceros_limpio = SpotifyandYoutubeClean(df_limpio).verificar_nulos_ceros()
print(resultados_nulos_ceros_limpio)

# Carga a SQLite
print("\n--- CARGANDO DATOS A SQLITE ---\n")
loader.to_sqlite()

# Mostrar gráficas al final

print("\n--- MOSTRANDO GRÁFICAS ---\n")
grafica_promedio_goles_liverpool(df_limpio, guardar=True)
grafica_promedio_tarjetas_por_equipo(df_limpio, guardar=True)
grafica_promedio_goles_por_equipo(df_limpio, guardar=True)
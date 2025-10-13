import pandas as pd
from typing import Union, List


def _read_csv_safe(path: str) -> pd.DataFrame:
	"""Lee un CSV intentando varios encodings si es necesario."""
	try:
		return pd.read_csv(path, encoding='utf-8', low_memory=False)
	except UnicodeDecodeError:
		try:
			return pd.read_csv(path, encoding='cp1252', low_memory=False)
		except Exception:
			return pd.read_csv(path, encoding='latin-1', low_memory=False)


def _normalize_top_text(s: object) -> str:
	"""Normalización simple para textos de Top*: convierte a str, reemplaza &amp;, lowercase, trim y colapsa espacios."""
	if pd.isna(s):
		return ''
	s2 = str(s)
	s2 = s2.replace('&amp;', '&')
	s2 = s2.replace('\u2019', "'")
	s2 = s2.lower().strip()
	s2 = ' '.join(s2.split())
	return s2


class LimpiezaTransform:
	"""Versión simple de transform: parseo de fechas, tipos y filtrado básico."""

	def __init__(self, df: pd.DataFrame):
		self.df = df.copy()

	def verificar_nulos_ceros(self) -> pd.DataFrame:
		nulos = self.df.isnull().sum()
		ceros = (self.df == 0).sum()
		return pd.DataFrame({'Nulos': nulos, 'Ceros': ceros})

	def clean_basic(self, drop_rows_without_date: bool = True, drop_rows_without_any_top: bool = False, label_fill: int = -1, normalize_top: bool = True, deduplicate: bool = True) -> pd.DataFrame:
		"""
		Limpieza básica:
		- Convierte `Date` a datetime.
		- Convierte `Label` a entero rellenando NaN con `label_fill`.
		- Opcional: elimina filas sin `Date`.
		- Opcional: elimina filas donde todas las columnas Top1..Top25 están vacías.
		- Normaliza texto en Top columns y deduplica por Date+Top* si se solicita.
		"""
		df = self.df.copy()

		if 'Date' in df.columns:
			df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

		if 'Label' in df.columns:
			df['Label'] = pd.to_numeric(df['Label'], errors='coerce').fillna(label_fill).astype(int)

		if drop_rows_without_date and 'Date' in df.columns:
			df = df.dropna(subset=['Date'])

		top_cols = [f'Top{i}' for i in range(1, 26) if f'Top{i}' in df.columns]
		if drop_rows_without_any_top and top_cols:
			df = df.dropna(subset=top_cols, how='all')

		# Normalizar textos de Top columns
		if normalize_top and top_cols:
			for c in top_cols:
				df[c] = df[c].apply(_normalize_top_text)

		# Deduplicado por Date + Top columns (si se solicita)
		if deduplicate and top_cols:
			subset = ['Date'] + top_cols if 'Date' in df.columns else top_cols
			df = df.drop_duplicates(subset=subset, keep='first')

		return df.reset_index(drop=True)


def full_clean_stock_sentiment(source: Union[str, pd.DataFrame], drop_rows_without_date: bool = True, drop_rows_without_any_top: bool = False, label_fill: int = -1, normalize_top: bool = True, deduplicate: bool = True) -> pd.DataFrame:
	"""
	Versión simplificada de la limpieza: carga (si se pasa path), aplica clean_basic y devuelve el DataFrame limpio.
	Mantiene las columnas Top1..Top25 tal cual están en el CSV original.
	"""
	if isinstance(source, str):
		df = _read_csv_safe(source)
	elif isinstance(source, pd.DataFrame):
		df = source.copy()
	else:
		raise ValueError('source debe ser ruta a CSV o un pd.DataFrame')

	lt = LimpiezaTransform(df)
	df_clean = lt.clean_basic(drop_rows_without_date=drop_rows_without_date, drop_rows_without_any_top=drop_rows_without_any_top, label_fill=label_fill, normalize_top=normalize_top, deduplicate=deduplicate)

	# resumen
	df_clean.attrs['cleaning_summary'] = {
		'original_rows': len(df),
		'final_rows': len(df_clean)
	}

	return df_clean
"""Genera gráficas de EDA para el dataset limpio.

Guarda los plots en `Extract/Graphic/plots/`.
Requiere: pandas, matplotlib, seaborn, numpy
"""
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def load_data(csv_path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path, parse_dates=["Date"])  # Date ya limpia
    return df


def plot_label_time_series(df: pd.DataFrame, out_dir: Path, show: bool = True):
    """Heatmap: en el eje Y los años 2000..2016, en el eje X Top1..Top25.

    Cada celda contiene el conteo de items no vacíos observados en ese Top por año.
    """
    df2 = df.copy()
    df2['Date'] = pd.to_datetime(df2['Date'])
    df2['year'] = df2['Date'].dt.year

    # limitar años
    df2 = df2[df2['year'].between(2000, 2016)]

    # top columns existentes (Top1..Top25)
    top_cols = [f'Top{i}' for i in range(1, 26) if f'Top{i}' in df2.columns]
    if not top_cols:
        raise ValueError('No se encontraron columnas Top1..Top25 en el DataFrame')

    # Para cada año y cada TopX, contar valores no vacíos
    counts = df2.groupby('year')[top_cols].agg(lambda col: col.fillna('').astype(str).str.strip().ne('').sum())

    # Asegurar que estén todos los años del 2000 al 2016 (incluir 0 si falta)
    years = list(range(2000, 2017))
    counts = counts.reindex(years, fill_value=0)

    plt.figure(figsize=(14, 8))
    sns.heatmap(counts, cmap='viridis', annot=True, fmt='d', cbar_kws={'label': 'Conteo items'})
    plt.title('Total de items no vacíos en Top1..Top25 por año')
    plt.ylabel('Año')
    plt.xlabel('Top (1..25)')
    plt.xticks(rotation=45)
    plt.tight_layout()

    out = Path(out_dir) / '01_label_time_series.png'
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out)
    if show:
        plt.show()
    plt.close()
    return out


def plot_label_distribution(df: pd.DataFrame, out_dir: Path, show: bool = True):
    """Distribución general de la variable Label (pie y bar)."""
    counts = df['Label'].value_counts().sort_index()
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    counts.plot(kind='bar', ax=axes[0], color=['#4c72b0', '#55a868'])
    axes[0].set_title('Conteo por Label (bar)')
    axes[0].set_xlabel('Label')
    counts.plot(kind='pie', ax=axes[1], autopct='%1.1f%%', startangle=90, legend=False)
    axes[1].set_ylabel('')
    axes[1].set_title('Distribución de Label (pie)')
    plt.tight_layout()
    out = Path(out_dir) / '02_label_distribution.png'
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out)
    if show:
        plt.show()
    plt.close()
    return out


def plot_top_tokens_frequency(df: pd.DataFrame, out_dir: Path, top_n=20, show: bool = True):
    """Gráfica: barras agrupadas por año con el conteo de cada Label.

    Para cada año presente en `Date` cuenta cuántos registros de cada `Label`
    existen y los muestra como barras agrupadas (una barra por label dentro de
    cada año).
    """
    df2 = df.copy()
    df2['Date'] = pd.to_datetime(df2['Date'], errors='coerce')
    df2 = df2.dropna(subset=['Date'])
    if 'Label' not in df2.columns:
        raise ValueError('No existe la columna "Label" en el DataFrame')

    df2['year'] = df2['Date'].dt.year

    # Agrupar por año y label
    counts = df2.groupby(['year', 'Label']).size().unstack(fill_value=0)
    if counts.empty:
        raise ValueError('No se encontraron datos para agrupar por año y Label')

    # Ordenar años
    counts = counts.sort_index()

    years = counts.index.astype(int).tolist()
    labels = counts.columns.tolist()

    x = np.arange(len(years))
    n_labels = max(1, len(labels))
    width = min(0.8, 0.8 / n_labels)

    plt.figure(figsize=(12, 6))
    for i, lab in enumerate(labels):
        vals = counts[lab].values
        plt.bar(x + i * width, vals, width=width, label=str(lab))

    plt.xlabel('Año')
    plt.ylabel('Conteo')
    plt.title('Conteo de Labels por año (barras agrupadas)')
    # Centrar ticks entre grupos
    if n_labels > 0:
        plt.xticks(x + (n_labels - 1) * width / 2, years, rotation=45)
    else:
        plt.xticks(x, years, rotation=45)

    plt.legend(title='Label')
    plt.tight_layout()

    out = Path(out_dir) / '03_label_by_year_grouped.png'
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out)
    if show:
        plt.show()
    plt.close()
    return out


def plot_top_words_by_position(df: pd.DataFrame, out_dir: Path, top_n: int = 20, show: bool = True):
    """Muestra un heatmap (posición Top1..TopN) × tokens (top global) con frecuencias.

    Calcula los `top_n` tokens más frecuentes en todas las columnas Top1..Top25 y luego
    construye una matriz con el conteo de esos tokens por cada posición Top.
    """
    # detectar columnas Top
    top_cols = [c for c in df.columns if c.lower().startswith('top')][:25]
    if not top_cols:
        raise ValueError('No se encontraron columnas Top1..Top25 en el DataFrame')

    # concatenar texto de los top cols para hallar tokens globales
    all_text = df[top_cols].fillna('').astype(str).agg(' '.join, axis=1)
    tokens = all_text.str.replace(',', ' ').str.split().explode()
    tokens = tokens.str.lower().str.replace(r"[^a-z0-9áéíóúñ']+", '', regex=True)
    tokens = tokens.replace('', np.nan).dropna()
    global_top = tokens.value_counts().nlargest(top_n).index.tolist()

    # construir matriz: filas = posiciones Top (Top1..TopM), columnas = tokens
    matrix = []
    positions = []
    for col in top_cols:
        col_tokens = df[col].fillna('').astype(str).str.replace(',', ' ').str.split().explode()
        col_tokens = col_tokens.str.lower().str.replace(r"[^a-z0-9áéíóúñ']+", '', regex=True)
        col_tokens = col_tokens.replace('', np.nan).dropna()
        vc = col_tokens.value_counts()
        row = [int(vc.get(tok, 0)) for tok in global_top]
        matrix.append(row)
        positions.append(col)

    mat_df = pd.DataFrame(matrix, index=positions, columns=global_top)

    plt.figure(figsize=(max(10, len(global_top) * 0.6), max(6, len(positions) * 0.4)))
    sns.heatmap(mat_df, cmap='magma', annot=True, fmt='d', cbar_kws={'label': 'Frecuencia'})
    plt.title(f'Frecuencia de top {top_n} tokens por posición Top (Top1..Top{len(top_cols)})')
    plt.ylabel('Posición Top')
    plt.xlabel('Tokens (top global)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    out = Path(out_dir) / '04_top_words_by_position.png'
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out)
    if show:
        plt.show()
    plt.close()
    return out


def plot_titles_per_month_2000(df: pd.DataFrame, out_dir: Path, show: bool = True):
    """Cuenta los días que tienen al menos un título (cualquier Top1..Top25 no vacío) por mes del año 2000.

    Eje X: meses (enero..diciembre). Eje Y: número de días dentro de ese mes donde al menos una posición Top estaba presente.
    """
    df2 = df.copy()
    df2['Date'] = pd.to_datetime(df2['Date'], errors='coerce')
    df2 = df2[df2['Date'].dt.year == 2000]
    if df2.empty:
        raise ValueError('No hay datos para el año 2000 en el dataset')

    top_cols = [c for c in df2.columns if c.lower().startswith('top')][:25]
    # marcar filas que tengan al menos un título no vacío en cualquiera de las posiciones Top
    has_title = df2[top_cols].fillna('').astype(str).apply(lambda row: row.str.strip().ne('').any(), axis=1)
    df2 = df2.assign(has_title=has_title.values)

    # agrupar por mes y contar días con has_title True (unique dates por día)
    df2['month'] = df2['Date'].dt.month
    # para cada día, queremos saber si ese día (Date) tuvo al menos un título -> agregación por date
    daily = df2.groupby(df2['Date'].dt.date)['has_title'].any().reset_index(name='has_title')
    daily['month'] = pd.to_datetime(daily['Date']).dt.month
    month_counts = daily.groupby('month')['has_title'].sum().reindex(range(1,13), fill_value=0)

    plt.figure(figsize=(10, 5))
    sns.barplot(x=month_counts.index, y=month_counts.values, palette='Blues')
    plt.title('Número de días con al menos un título por mes (Año 2000)')
    plt.xlabel('Mes (1=Ene, 12=Dic)')
    plt.ylabel('Número de días con títulos')
    plt.xticks(ticks=range(0,12), labels=[1,2,3,4,5,6,7,8,9,10,11,12])
    plt.tight_layout()

    out = Path(out_dir) / '05_titles_per_month_2000.png'
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out)
    if show:
        plt.show()
    plt.close()
    return out

def generate_all_plots(csv_path: str | Path, out_dir: str | Path = None, show: bool = True):
    """Genera y guarda los plots. Por defecto guarda en `Docs/plots` y muestra ventanas si show=True.

    Args:
        csv_path: ruta al CSV limpio.
        out_dir: directorio donde guardar las imágenes. Si None, usa `Docs/plots` en la raíz del repo.
        show: si True, llamará a plt.show() para que las gráficas aparezcan en ventanas.
    Returns:
        lista de rutas guardadas.
    """
    df = load_data(csv_path)
    # determinar out_dir por defecto: ../../.. -> repo root
    if out_dir is None:
        # file is at <repo>/Extract/Graphic/LimpiezaGraphic.py -> repo root is parents[2]
        repo_root = Path(__file__).resolve().parents[2]
        out_dir = repo_root / 'Docs'
    out_dir = Path(out_dir)

    results = []
    results.append(plot_label_time_series(df, out_dir=out_dir, show=show))
    results.append(plot_label_distribution(df, out_dir=out_dir, show=show))
    results.append(plot_top_tokens_frequency(df, out_dir=out_dir, top_n=25, show=show))
    results.append(plot_top_words_by_position(df, out_dir=out_dir, top_n=20, show=show))
    results.append(plot_titles_per_month_2000(df, out_dir=out_dir, show=show))
    return results


if __name__ == '__main__':
    import sys
    csv = Path(__file__).parent.parent / 'Files' / 'output_clean.csv'
    if len(sys.argv) > 1:
        csv = Path(sys.argv[1])
    print('Cargando datos desde:', csv)
    outs = generate_all_plots(csv, out_dir=None, show=True)
    print('Plots guardados:')
    for o in outs:
        print('-', o)

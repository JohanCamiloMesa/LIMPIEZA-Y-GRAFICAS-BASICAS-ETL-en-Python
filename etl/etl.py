"""Simple ETL script: extract CSVs from data/raw, transform, and load cleaned data to data/clean and SQLite."""
from pathlib import Path
import pandas as pd
import sqlite3

RAW_DIR = Path(__file__).resolve().parents[1] / 'data' / 'raw'
CLEAN_DIR = Path(__file__).resolve().parents[1] / 'data' / 'clean'
CLEAN_DIR.mkdir(parents=True, exist_ok=True)


def extract_all_csv(raw_dir=RAW_DIR):
    csvs = list(raw_dir.glob('*.csv'))
    if not csvs:
        raise FileNotFoundError(f'No CSV files found in {raw_dir}')
    dfs = [pd.read_csv(f) for f in csvs]
    return pd.concat(dfs, ignore_index=True)


def transform(df: pd.DataFrame) -> pd.DataFrame:
    # Standardize column names
    df = df.rename(columns=lambda s: s.strip().lower())

    # Parse dates with multiple formats
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce', dayfirst=False)

    # Trim strings and normalize case
    for col in ['city', 'product']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace({'nan': None})
            df[col] = df[col].where(df[col].notnull(), None)

    # Normalize city names (title case)
    if 'city' in df.columns:
        df['city'] = df['city'].dropna().astype(str).str.title()

    # Convert numeric columns
    for col in ['quantity']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

    for col in ['price']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Create derived column: total_amount
    if set(['quantity','price']).issubset(df.columns):
        df['total_amount'] = df['quantity'].astype(float).fillna(0) * df['price'].fillna(0.0)

    # Drop exact duplicates
    df = df.drop_duplicates()

    # Handle missing product/customer
    if 'product' in df.columns:
        df['product'] = df['product'].fillna('Unknown')
    if 'customer_id' in df.columns:
        df['customer_id'] = pd.to_numeric(df['customer_id'], errors='coerce').astype('Int64')

    return df


def load_outputs(df: pd.DataFrame, clean_dir=CLEAN_DIR):
    csv_path = clean_dir / 'cleaned_sales.csv'
    parquet_path = clean_dir / 'cleaned_sales.parquet'
    sqlite_path = clean_dir / 'cleaned_sales.sqlite'

    df.to_csv(csv_path, index=False)
    df.to_parquet(parquet_path, index=False)

    # Save to SQLite
    conn = sqlite3.connect(sqlite_path)
    df.to_sql('sales', conn, if_exists='replace', index=False)
    conn.close()

    return {'csv': str(csv_path), 'parquet': str(parquet_path), 'sqlite': str(sqlite_path)}


if __name__ == '__main__':
    print('Running ETL...')
    df_raw = extract_all_csv()
    print(f'Extracted rows: {len(df_raw)}')
    df_clean = transform(df_raw)
    print(f'Cleaned rows: {len(df_clean)}')
    outs = load_outputs(df_clean)
    print('Saved outputs:')
    for k, v in outs.items():
        print(k, v)

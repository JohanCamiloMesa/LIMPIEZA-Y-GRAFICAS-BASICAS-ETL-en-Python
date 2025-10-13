import requests
import pandas as pd
import numpy as np

class LimpiezaExtract:  

    def __init__(self, csv_path):
        self.csv = csv_path
        self.data = None

    def queries(self):
        # Intentar leer con distintos encodings para evitar errores de decoding
        try:
            self.data = pd.read_csv(self.csv, encoding='utf-8', low_memory=False)
        except UnicodeDecodeError:
            try:
                self.data = pd.read_csv(self.csv, encoding='cp1252', low_memory=False)
            except Exception:
                # último recurso
                self.data = pd.read_csv(self.csv, encoding='latin-1', low_memory=False)
        except Exception as e:
            # Propagar con mensaje más claro
            raise RuntimeError(f"No se pudo leer el CSV '{self.csv}': {e}")

    def response(self):
        return self.data.head(5)
    
    def info(self):
        return self.data.info()
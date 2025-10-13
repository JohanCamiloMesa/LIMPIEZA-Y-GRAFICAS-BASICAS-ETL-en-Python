import requests
import pandas as pd
import numpy as np

class SpotifyandYoutubeExtract:  

    def __init__(self, csv_path):
        self.csv = csv_path

    def queries(self):
        self.data = pd.read_csv(self.csv)

    def response(self):
        return self.data.head(5)
    
    def info(self):
        return self.data.info()
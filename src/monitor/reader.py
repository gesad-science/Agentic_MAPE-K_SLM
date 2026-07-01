import pandas as pd

class CSVReader:
    def __init__(self, file):
        self.df = pd.read_csv(file)
        self.index = 0

    def next(self):
        if self.index >= len(self.df):
            return None
        row = self.df.iloc[self.index]
        self.index += 1
        return row
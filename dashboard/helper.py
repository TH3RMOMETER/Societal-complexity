from math import hypot
from dataclasses import dataclass

import pandas as pd

@dataclass
class Vector:
    x: float
    y: float

    def __abs__(self):
        return hypot(self.x, self.y)

def preprocess(path):
    dataset = pd.read_parquet(path)
    dataset['wind'] = dataset[['u_pred', 'v_pred']].apply(lambda x: Vector(x[0], x[1]).__abs__(), axis=1)
    dataset['norm_wind'] = (dataset.wind - dataset.wind.min()) / (dataset.wind.max() - dataset.wind.min()) * 0.5
    dataset = dataset.reset_index(drop=True)
    return dataset

if __name__ == '__main__':
    preprocess(r'/Users/yvette/Coding/SCDD/Societal-complexity/dashboard/dataset_with_preds.parquet')
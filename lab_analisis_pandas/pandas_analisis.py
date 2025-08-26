import pandas as pd
import numpy as np
from datetime import date

data_frame = pd.read_csv('lab_analisis_pandas/train.csv')

print(data_frame.head())

print(data_frame.info())

print(data_frame.isna().sum())

data_frame = data_frame.assign(birthday=lambda x: date.today().year - x['age'])

data_frame['education'] = data_frame['education'].fillna('Unknown')

data_frame = data_frame.dropna(subset=['previous_year_rating']).reset_index(drop=True)
data_frame['gender'] = np.where(data_frame['gender'] == 'm', 'Masculino', 'Femenino')

print(data_frame.describe())
print(data_frame.head()['gender'])

filtered_df = data_frame.query('length_of_service > 5').reset_index(drop=True)

grouped = filtered_df.groupby('department').agg(
    avg_training_score=('avg_training_score', 'mean'),
    promoted_count=('is_promoted', 'sum')
).reset_index()

grouped.to_csv('lab_analisis_pandas/summary_by_department.csv', index=False)

print(grouped)
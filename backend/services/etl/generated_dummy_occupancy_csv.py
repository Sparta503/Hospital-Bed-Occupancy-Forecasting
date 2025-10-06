import pandas as pd
import numpy as np

df = pd.DataFrame({
    "hospital_id": [f"HOSP{i%5+1}" for i in range(50)],
    "ward_id": [f"WARD{i%3+1}" for i in range(50)],
    "record_date": pd.date_range("2023-01-01", periods=50, freq="D"),
    "occupied_beds": np.random.randint(10, 50, size=50)
})

df.to_csv("occupancy_data.csv", index=False)
print("occupancy_data.csv generated with 50 samples.")

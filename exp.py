from pathlib import Path

import polars as pl

scores_dir = Path("scores")

for score_file in scores_dir.iterdir():
    df = pl.read_parquet(score_file)
    print(df)

import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('DB_USER', 'dbt_user')}:{os.getenv('DB_PASSWORD', 'dbt_pass')}"
    f"@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'people_analytics')}"
)

TABLES = {
    "job_requisitions": "data/raw/job_requisitions.csv",
    "candidates": "data/raw/candidates.csv",
    "pipeline_stages": "data/raw/pipeline_stages.csv",
    "offers": "data/raw/offers.csv",
}

if __name__ == "__main__":
    with engine.begin() as conn:
        conn.exec_driver_sql("CREATE SCHEMA IF NOT EXISTS raw;")
    for table, path in TABLES.items():
        df = pd.read_csv(path)
        df.to_sql(table, engine, schema="raw", if_exists="replace", index=False)
        print(f"Loaded raw.{table} ({len(df)} rows)")

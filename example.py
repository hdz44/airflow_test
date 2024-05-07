from airflow import DAG
from datetime import datetime

# Define the DAG
dag = DAG(
    dag_id="test_dag",
    description="just dag!!'",
    start_date=datetime(2023, 7, 1),
    schedule_interval="@daily",
    catchup=False,
)

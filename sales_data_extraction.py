from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.hooks.postgres_hook import PostgresHook
import random

default_args = {
    'owner': 'sales',
    'depends_on_past': False,
    'start_date': datetime(2024, 2, 27),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 81,
    'retry_delay': timedelta(minutes=1),
}

dag = DAG(
    'sales_data_extraction',
    default_args=default_args,
    description='Extract and load daily sales data into PostgreSQL',
    schedule_interval=timedelta(days=1),
    catchup=False,
)


def generate_sales_data():
    """Generate random sales data."""
    products = ['Product_lol', 'Product_BG', 'Product_CEA']
    sales_data = [(random.choice(products), random.randint(
        1, 20), (datetime.now() - timedelta(days=1)).date().strftime('%Y-%m-%d'))for _ in range(10)]
    return sales_data


def insert_sales_data(**kwargs):
    """Insert sales data into PostgreSQL."""
    ti = kwargs['ti']
    sales_data = ti.xcom_pull(task_ids='generate_sales_data')
    pg_hook = PostgresHook(postgres_conn_id='example_db')
    insert_query = """
    INSERT INTO daily_sales (product, quantity_sold, sales_date)
    VALUES (%s, %s, %s);
    """
    for data in sales_data:
        pg_hook.run(insert_query, parameters=data)


create_sales_table = PostgresOperator(
    task_id='create_sales_table',
    postgres_conn_id='example_db',
    sql="""
    CREATE TABLE IF NOT EXISTS daily_sales (
        id SERIAL PRIMARY KEY,
        product VARCHAR(245),
        quantity_sold INT,
        sales_date DATE
    );
    """,
    dag=dag,
)

generate_sales_data_task = PythonOperator(
    task_id='generate_sales_data',
    python_callable=generate_sales_data,
    dag=dag,
)

insert_sales_data_task = PythonOperator(
    task_id='insert_sales_data',
    python_callable=insert_sales_data,
    provide_context=True,
    dag=dag,
)

create_sales_table >> generate_sales_data_task >> insert_sales_data_task

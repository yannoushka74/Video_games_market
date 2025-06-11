from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator

default_args = {
    'owner': 'admin',
    'depends_on_past': False,
    'start_date': datetime(2025, 6, 11),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'hello_world',
    default_args=default_args,
    description='Un DAG simple de test',
    schedule_interval=timedelta(days=1),
    catchup=False,
)

start = DummyOperator(
    task_id='start',
    dag=dag,
)

end = DummyOperator(
    task_id='end',
    dag=dag,
)
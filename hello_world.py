from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator

def git_sync_test():
    print("DAG synchronisé depuis Git avec succès!")
    return "Git sync works!"

default_args = {
    'owner': 'admin',
    'depends_on_past': False,
    'start_date': datetime(2025, 6, 11),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'git_sync_test_dag',
    default_args=default_args,
    description='DAG de test pour GitSync',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['git-sync', 'test'],
)

start_task = DummyOperator(
    task_id='start_git_sync',
    dag=dag,
)

test_task = PythonOperator(
    task_id='test_git_sync',
    python_callable=git_sync_test,
    dag=dag,
)

end_task = DummyOperator(
    task_id='end_git_sync',
    dag=dag,
)
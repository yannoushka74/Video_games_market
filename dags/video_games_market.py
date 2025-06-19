from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def hello():
    print("✅ DAG synchronisé depuis Git avec succès !")

with DAG(
    dag_id="pl_main_market",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,  # Pas d'exécution automatique
    catchup=False,
    tags=["test", "git-sync"],
) as dag:
    
    task = PythonOperator(
        task_id="say_hello",
        python_callable=hello,
    )

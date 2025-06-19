"""
DAG pour le traitement des données de jeux vidéo avec Docker
Version finale corrigée avec le bon nom d'image
"""

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta

# Configuration du DAG
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'max_active_runs': 1,
}

# Configuration Docker commune
DOCKER_CONFIG = {
    'docker_url': 'unix://var/run/docker.sock',
    'network_mode': 'bridge',
    'auto_remove': 'success',
    'force_pull': False,
    'mount_tmp_dir': False,
    'tty': True,
}

# Variables d'environnement communes
BASE_ENVIRONMENT = {
    'EXECUTION_DATE': '{{ ds }}',
    'RUN_ID': '{{ run_id }}',
    'DAG_ID': '{{ dag.dag_id }}',
    'TASK_ID': '{{ task.task_id }}',
    'LOG_LEVEL': 'INFO',
    'PYTHONUNBUFFERED': '1',
}

# NOM D'IMAGE CORRECT
IMAGE_NAME = 'python-videogames-processor:latest'

with DAG(
    dag_id='video_games_market_pipeline',
    default_args=default_args,
    description='Pipeline de traitement des données de jeux vidéo avec Docker',
    schedule_interval=None,
    catchup=False,
    max_active_runs=1,
    tags=['videogames', 'docker', 'data-processing'],
    doc_md=__doc__,
) as dag:
    
    # Tâche de démarrage
    start_task = DummyOperator(
        task_id='start_pipeline',
        doc_md="Point de départ du pipeline"
    )
    
    # Vérification de l'image Docker
    check_image = DockerOperator(
        task_id='check_docker_image',
        image=IMAGE_NAME,
        command='python -c "print(\'🐳 Image Docker disponible\'); import sys; sys.exit(0)"',
        environment={
            **BASE_ENVIRONMENT,
            'TASK_TYPE': 'check'
        },
        **DOCKER_CONFIG,
        mem_limit='256m',
        cpus=0.1,
        execution_timeout=timedelta(minutes=2),
        doc_md="Vérification que l'image Docker est disponible localement"
    )
    
    # Préparation de l'environnement
    prepare_environment = DockerOperator(
        task_id='prepare_environment',
        image=IMAGE_NAME,
        command='python main.py',
        environment={
            **BASE_ENVIRONMENT,
            'TASK_TYPE': 'preparation',
            'LOG_LEVEL': 'INFO',
        },
        **DOCKER_CONFIG,
        mem_limit='1g',
        cpus=0.5,
        execution_timeout=timedelta(minutes=10),
        doc_md="Préparation de l'environnement et vérification des dépendances"
    )
    
    # Traitement principal
    process_videogames = DockerOperator(
        task_id='process_videogames_data',
        image=IMAGE_NAME,
        command='python main.py',
        environment={
            **BASE_ENVIRONMENT,
            'TASK_TYPE': 'main',
            'LOG_LEVEL': 'INFO',
        },
        **DOCKER_CONFIG,
        mem_limit='2g',
        cpus=1.0,
        execution_timeout=timedelta(minutes=30),
        doc_md="Traitement principal des données de jeux vidéo"
    )
    
    # Nettoyage
    cleanup_data = DockerOperator(
        task_id='cleanup_data',
        image=IMAGE_NAME,
        command='python main.py',
        environment={
            **BASE_ENVIRONMENT,
            'TASK_TYPE': 'cleanup',
            'LOG_LEVEL': 'INFO',
        },
        **DOCKER_CONFIG,
        mem_limit='512m',
        cpus=0.25,
        execution_timeout=timedelta(minutes=5),
        trigger_rule='all_done',
        doc_md="Nettoyage des fichiers temporaires et finalisation"
    )
    
    # Tâche de fin
    end_task = DummyOperator(
        task_id='end_pipeline',
        trigger_rule='all_done',
        doc_md="Fin du pipeline"
    )
    
    # Définition des dépendances
    start_task >> check_image >> prepare_environment >> process_videogames >> cleanup_data >> end_task

# Test du DAG
if __name__ == '__main__':
    print("🔍 Validation du DAG...")
    print(f"DAG ID: {dag.dag_id}")
    print(f"Image utilisée: {IMAGE_NAME}")
    print(f"Nombre de tâches: {len(dag.tasks)}")
    print("✅ DAG valide!")
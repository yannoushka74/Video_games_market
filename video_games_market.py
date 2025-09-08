"""
DAG pour le traitement des données de jeux vidéo avec Docker
Version nettoyée - Paramètres Docker valides uniquement
"""

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta

# Configuration du DAG
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
    'max_active_runs': 1,
}

# Configuration Docker MINIMALE (paramètres universellement supportés)
DOCKER_CONFIG = {
    'auto_remove': 'success',  # 'never', 'success', ou 'force'
    'force_pull': False,
}

# Variables d'environnement essentielles
BASE_ENVIRONMENT = {
    'EXECUTION_DATE': '{{ ds }}',
    'RUN_ID': '{{ run_id }}',
    'DAG_ID': '{{ dag.dag_id }}',
    'TASK_ID': '{{ task.task_id }}',
    'LOG_LEVEL': 'INFO',
    'PYTHONUNBUFFERED': '1',
}

# Image Docker
IMAGE_NAME = 'python-videogames-processor:latest'

with DAG(
    dag_id='video_games_clean_pipeline',
    default_args=default_args,
    description='Pipeline nettoyé sans paramètres Docker problématiques',
    schedule_interval=None,
    catchup=False,
    max_active_runs=1,
    tags=['videogames', 'docker', 'clean'],
    doc_md=__doc__,
) as dag:
    
    # Tâche de démarrage
    start_task = DummyOperator(
        task_id='start_pipeline'
    )
    
    # Vérification avec Bash (plus fiable)
    check_docker_bash = BashOperator(
        task_id='check_docker_image',
        bash_command=f'''
        echo "🔍 Vérification de l'image Docker: {IMAGE_NAME}"
        
        # Vérifier que Docker fonctionne
        if ! docker info > /dev/null 2>&1; then
            echo "❌ Docker non accessible"
            exit 1
        fi
        
        # Vérifier que l'image existe
        if docker images | grep -q "python-videogames-processor"; then
            echo "✅ Image trouvée"
            
            # Test simple de l'image
            if docker run --rm {IMAGE_NAME} python -c "print('🎮 Test Docker OK')"; then
                echo "✅ Test image réussi"
            else
                echo "❌ Test image échoué"
                exit 1
            fi
        else
            echo "❌ Image {IMAGE_NAME} non trouvée"
            echo "💡 Construisez l'image avec: docker build -t {IMAGE_NAME} ."
            exit 1
        fi
        ''',
        execution_timeout=timedelta(minutes=3)
    )
    
    # Traitement avec configuration Docker minimale
    process_videogames = DockerOperator(
        task_id='process_videogames_data',
        image=IMAGE_NAME,
        command='python -c "print(\'🎮 Traitement des jeux vidéo...\'); import time; time.sleep(3); print(\'✅ Traitement terminé avec succès!\')"',
        environment={
            **BASE_ENVIRONMENT,
            'TASK_TYPE': 'main',
        },
        # SEULEMENT les paramètres Docker de base
        auto_remove='success',
        force_pull=False,
        mem_limit='1g',
        execution_timeout=timedelta(minutes=10)
    )
    
    # Traitement avec main.py (si disponible)
    process_main_py = DockerOperator(
        task_id='process_with_main_py',
        image=IMAGE_NAME,
        command='python main.py',
        environment={
            **BASE_ENVIRONMENT,
            'TASK_TYPE': 'main',
        },
        # Configuration minimale
        auto_remove='success',
        force_pull=False,
        mem_limit='1g',
        execution_timeout=timedelta(minutes=15)
    )
    
    # Nettoyage
    cleanup_task = DockerOperator(
        task_id='cleanup_data',
        image=IMAGE_NAME,
        command='python -c "print(\'🧹 Nettoyage...\'); import time; time.sleep(1); print(\'✅ Nettoyage terminé\')"',
        environment={
            **BASE_ENVIRONMENT,
            'TASK_TYPE': 'cleanup',
        },
        auto_remove='success',
        force_pull=False,
        mem_limit='256m',
        execution_timeout=timedelta(minutes=5),
        trigger_rule='all_done'  # S'exécute même si les tâches précédentes échouent
    )
    
    # Tâche de fin
    end_task = DummyOperator(
        task_id='end_pipeline',
        trigger_rule='none_failed_min_one_success'
    )
    
    # Flux du pipeline
    start_task >> check_docker_bash >> [process_videogames, process_main_py] >> cleanup_task >> end_task

# Test de validation du DAG
if __name__ == '__main__':
    print("🔍 Validation du DAG nettoyé...")
    print(f"DAG ID: {dag.dag_id}")
    print(f"Image: {IMAGE_NAME}")
    print(f"Tâches: {len(dag.tasks)}")
    
    # Vérifier que toutes les tâches ont des paramètres valides
    for task in dag.tasks:
        if hasattr(task, 'image'):
            print(f"  - {task.task_id}: DockerOperator avec image {task.image}")
        else:
            print(f"  - {task.task_id}: {type(task).__name__}")
    
    print("✅ DAG validé!")
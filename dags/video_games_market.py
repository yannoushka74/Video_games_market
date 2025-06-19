"""
DAG simplifié pour éviter les problèmes de réseau/DNS
Version compatible avec tous les executors
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
    'retries': 1,  # Réduit pour éviter les problèmes
    'retry_delay': timedelta(minutes=2),
    'max_active_runs': 1,
}

# Configuration Docker simplifiée (sans réseau complexe)
DOCKER_CONFIG_SIMPLE = {
    'auto_remove': 'success',
    'force_pull': False,
    'tty': False,  # Désactivé pour éviter les problèmes
    'stdin_open': False,
}

# Variables d'environnement essentielles seulement
SIMPLE_ENVIRONMENT = {
    'TASK_TYPE': 'main',
    'LOG_LEVEL': 'INFO',
    'PYTHONUNBUFFERED': '1',
}

IMAGE_NAME = 'python-videogames-processor:latest'

with DAG(
    dag_id='video_games_simple_pipeline',
    default_args=default_args,
    description='Pipeline simplifié sans problèmes réseau',
    schedule_interval=None,
    catchup=False,
    max_active_runs=1,
    tags=['videogames', 'docker', 'simple'],
    doc_md=__doc__,
) as dag:
    
    # Tâche de démarrage
    start_task = DummyOperator(
        task_id='start_pipeline'
    )
    
    # Test avec BashOperator (plus fiable)
    test_docker_bash = BashOperator(
        task_id='test_docker_availability',
        bash_command=f'''
        echo "🔍 Test de l'image Docker {IMAGE_NAME}"
        
        # Vérifier que l'image existe
        if docker images | grep -q "python-videogames-processor"; then
            echo "✅ Image trouvée"
            
            # Test simple de l'image
            docker run --rm {IMAGE_NAME} python -c "print('🎮 Docker Test OK')"
            
            if [ $? -eq 0 ]; then
                echo "✅ Test Docker réussi"
                exit 0
            else
                echo "❌ Test Docker échoué"
                exit 1
            fi
        else
            echo "❌ Image non trouvée"
            exit 1
        fi
        ''',
        execution_timeout=timedelta(minutes=3)
    )
    
    # Traitement principal avec configuration minimale
    process_videogames = DockerOperator(
        task_id='process_videogames_data',
        image=IMAGE_NAME,
        command='python -c "print(\'🎮 Traitement des jeux vidéo\'); import time; time.sleep(2); print(\'✅ Terminé\')"',
        environment=SIMPLE_ENVIRONMENT,
        **DOCKER_CONFIG_SIMPLE,
        mem_limit='1g',
        execution_timeout=timedelta(minutes=5)
    )
    
    # Alternative avec main.py si disponible
    process_with_main = DockerOperator(
        task_id='process_with_main_py',
        image=IMAGE_NAME,
        command='python main.py',
        environment={
            **SIMPLE_ENVIRONMENT,
            'TASK_TYPE': 'main',
        },
        **DOCKER_CONFIG_SIMPLE,
        mem_limit='1g',
        execution_timeout=timedelta(minutes=10)
    )
    
    # Tâche de fin
    end_task = DummyOperator(
        task_id='end_pipeline',
        trigger_rule='none_failed_min_one_success'
    )
    
    # Flux simplifié
    start_task >> test_docker_bash >> [process_videogames, process_with_main] >> end_task
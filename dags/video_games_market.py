from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime, timedelta

# Configuration du DAG
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id="pl_main_buy_videogames",
    default_args=default_args,
    schedule_interval=None,  # Pas d'exécution automatique
    catchup=False,
    tags=["videogames", "git-sync", "docker", "local"],
    description="Pipeline d'achat de jeux vidéo avec Docker local"
) as dag:
    
    # Tâche principale avec DockerOperator (IMAGE LOCALE)
    process_videogames = DockerOperator(
        task_id="process_buy_videogames",
        image="python-videogames-processor:latest",  # Image locale uniquement
        
        # Configuration Docker locale
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        auto_remove=True,
        force_pull=False,  # Important : ne pas essayer de pull depuis un registry
        
        # Variables d'environnement pour le script
        environment={
            'EXECUTION_DATE': '{{ ds }}',
            'RUN_ID': '{{ run_id }}',
            'DAG_ID': '{{ dag.dag_id }}',
            'TASK_ID': '{{ task.task_id }}',
            'LOG_LEVEL': 'INFO',
            'TASK_TYPE': 'main',
        },
        
        # Ressources et limites
        mem_limit='2g',
        cpus=1.0,
        
        # Timeout
        timeout=1800,  # 30 minutes
        execution_timeout=timedelta(hours=1),
        
        # PAS de docker_conn_id car c'est local
        # docker_conn_id='docker_registry_conn',  # Commenté pour local
    )
    
    # Tâche de préparation
    prepare_environment = DockerOperator(
        task_id="prepare_environment",
        image="python-videogames-processor:latest",  # Même image locale
        
        environment={
            'TASK_TYPE': 'preparation',
            'LOG_LEVEL': 'DEBUG',
            'EXECUTION_DATE': '{{ ds }}',
        },
        
        auto_remove=True,
        force_pull=False,  # Pas de pull
        mem_limit='1g',
        cpus=0.5,
        timeout=300,  # 5 minutes
    )
    
    # Tâche de nettoyage
    cleanup_data = DockerOperator(
        task_id="cleanup_data",
        image="python-videogames-processor:latest",  # Même image locale
        
        environment={
            'TASK_TYPE': 'cleanup',
            'EXECUTION_DATE': '{{ ds }}',
        },
        
        auto_remove=True,
        force_pull=False,  # Pas de pull
        mem_limit='512m',
        cpus=0.25,
        timeout=300,
        
        # Cette tâche s'exécute même si la précédente échoue
        trigger_rule='all_done',
    )
    
    # Définition des dépendances
    prepare_environment >> process_videogames >> cleanup_data
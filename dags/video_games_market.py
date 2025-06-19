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
    tags=["videogames", "git-sync", "docker"],
    description="Pipeline d'achat de jeux vidéo avec Docker et Git"
) as dag:
    
    # Tâche principale avec DockerOperator
    process_videogames = DockerOperator(
        task_id="process_buy_videogames",
        image="python-videogames-processor:latest",  # À remplacer par votre image
        
        # Configuration Docker
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        auto_remove=True,
        force_pull=False,
        
        # Variables d'environnement pour le script
        environment={
            'EXECUTION_DATE': '{{ ds }}',
            'RUN_ID': '{{ run_id }}',
            'DAG_ID': '{{ dag.dag_id }}',
            'TASK_ID': '{{ task.task_id }}',
            'LOG_LEVEL': 'INFO',
            'GIT_BRANCH': 'main',  # ou via une Variable Airflow
        },
        
        # Ressources et limites
        mem_limit='2g',
        cpus=1.0,
        
        # Timeout
        timeout=1800,  # 30 minutes
        execution_timeout=timedelta(hours=1),
        
        # Volumes si nécessaire (optionnel)
        # mounts=[
        #     Mount(source='/opt/airflow/data', target='/app/data', type='bind', read_only=True),
        #     Mount(source='/opt/airflow/output', target='/app/output', type='bind')
        # ],
        
        # Configuration de connexion Docker (si registre privé)
        # docker_conn_id='docker_registry_conn',
    )
    
    # Optionnel : Tâche de préparation
    prepare_environment = DockerOperator(
        task_id="prepare_environment",
        image="python-videogames-processor:latest",
        command=["python", "-c", "print('🔧 Environnement préparé pour le traitement des jeux vidéo')"],
        
        environment={
            'TASK_TYPE': 'preparation',
            'LOG_LEVEL': 'DEBUG',
        },
        
        auto_remove=True,
        mem_limit='1g',
        cpus=0.5,
        timeout=300,  # 5 minutes
    )
    
    # Optionnel : Tâche de nettoyage
    cleanup_data = DockerOperator(
        task_id="cleanup_data",
        image="python-videogames-processor:latest",
        command=["python", "-c", "print('🧹 Nettoyage terminé')"],
        
        environment={
            'TASK_TYPE': 'cleanup',
            'EXECUTION_DATE': '{{ ds }}',
        },
        
        auto_remove=True,
        mem_limit='512m',
        cpus=0.25,
        timeout=300,
        
        # Cette tâche s'exécute même si la précédente échoue
        trigger_rule='all_done',
    )
    
    # Définition des dépendances
    prepare_environment >> process_videogames >> cleanup_data
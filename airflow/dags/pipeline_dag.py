from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {"retries": 2, "retry_delay": timedelta(minutes=1)}

with DAG(
    "pipeline_health_dag",
    default_args=default_args,
    schedule=timedelta(minutes=5),
    start_date=datetime(2026, 1, 1),
    catchup=False,
) as dag:

    run_dbt = BashOperator(
        task_id="run_dbt_models",
        bash_command=(
            "pip install --quiet dbt-postgres && "
            "cd /opt/airflow/dbt_project && "
            "dbt run --profiles-dir /opt/airflow/dbt_profiles --target docker"
        ),
    )

    detect_anomalies = BashOperator(
        task_id="detect_anomalies",
        bash_command="DB_HOST=host.docker.internal python3 /opt/airflow/anomaly_detection/detect_anomalies.py",
    )

    run_dbt >> detect_anomalies
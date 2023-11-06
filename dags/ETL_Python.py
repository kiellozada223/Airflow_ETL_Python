from datetime import timedelta
from airflow import DAG 
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago 
import os
import requests
import shutil

dag_path = os.getcwd()

default_args = {
    'owner': 'Mike Lozada',
    'start_date':  days_ago(5)
}

etl_dag = DAG(
    'ETL_Processing',
    default_args=default_args,
    description='My Second DAG',
    schedule_interval=timedelta(days=1)
)

def download():
    url = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DB0250EN-SkillsNetwork/labs/Apache%20Airflow/Build%20a%20DAG%20using%20Airflow/web-server-access-log.txt"
    response = requests.get(url, stream=True)
    file_path = "/opt/airflow/raw_data/web-server-access-log.txt"
    
    with open(file_path, 'wb') as file:
        shutil.copyfileobj(response.raw, file)


download = PythonOperator(
    task_id='download',
    python_callable=download,
    provide_context=True,
    dag=etl_dag
)


extract = BashOperator(
    task_id = 'extract',
    bash_command= 'cut -f1,4 -d"#" /opt/airflow/raw_data/web-server-access-log.txt > /opt/airflow/processed_data/extracted.txt',
    dag = etl_dag
)

transform = BashOperator(
    task_id = 'transform',
    bash_command='tr "[a-z]" "[A-Z]" < /opt/airflow/processed_data/extracted.txt > /opt/airflow/processed_data/capitalized.txt',
    dag = etl_dag
)

load =  BashOperator(
    task_id = 'load',
    bash_command='tar -czvf capitalized.txt.tar.gz /opt/airflow/processed_data',
    dag = etl_dag
)

download >> extract >> transform >> load
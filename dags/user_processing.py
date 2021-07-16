
# import modules
from airflow.models import DAG
from airflow.providers.sqlite.operators.sqlite import SqliteOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator
from datetime import datetime
from airflow.operators.python import PythonOperator
from pandas import json_normalize
import pandas as pd
from airflow.operators.bash import BashOperator
import json


default_args = {
        'start_date':datetime(2021,1,1) 
        }

def _read_the_file(**kwargs):
    df = pd.read_csv('/tmp/processed_user.csv')

def _processing_user(ti):
    users = ti.xcom_pull(task_ids=['extracting_user'])
    if not len(users) or 'results' not in users[0]:
        raise ValueError('User is empty')
    user = users[0]['results'][0]
    processed_user = json_normalize({
            'firstname':user['name']['first'],
            'lastname': user['name']['last'],
            'country': user['location']['country'],
            'username': user['login']['username'],
            'password': user['login']['password'],
            'email': user['email']
            })
    processed_user.to_csv('/tmp/processed_user.csv', index=None, header=False)

with DAG('user_processing', schedule_interval=None, default_args=default_args, catchup=False) as dag:
    # define the tasks/operators here
    creating_table = SqliteOperator(
            task_id = 'creating_table',
            sqlite_conn_id='db_sqlite',
            sql=''' create table if not exists users (
            firstname text not null, lastname text not null, country text not null,
            username text not null, email text not null primary key);
            '''
            )

    is_api_available = HttpSensor(
            task_id='is_api_available',
            http_conn_id='user_api',
            endpoint = 'api/'
            )

    extracting_user = SimpleHttpOperator(
            task_id = 'extracting_user',
            http_conn_id = 'user_api',
            endpoint = 'api/',
            method='GET',
            response_filter = lambda response: json.loads(response.text),
            log_response=True
            )
    processing_user = PythonOperator(
            task_id = 'Processing_user',
            python_callable=_processing_user
            )

    storing_user = PythonOperator(
            task_id = 'Storing_user',
            python_callable=_read_the_file,
            op_kwargs={'Key1':'Value1', 'Key2':'Value2'}
            )

    creating_table >> is_api_available >> extracting_user >> processing_user >> storing_user





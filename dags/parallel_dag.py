from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import BranchPythonOperator
from datetime import datetime
from airflow.utils.task_group import TaskGroup
from airflow.operators.python import PythonOperator

def _task2_fun(ti):
    print('This is task 2 function')
    x = 24
    ti.xcom_push(key='task2_return', value = x)

def _task3_fun(ti):
    print('This is task 3 function')
    y = ti.xcom_pull(key='task2_return', task_ids=['processing_tasks.task_2'])
    print(f'Value recived is {y}')

def _call_function(ti):
    return 'task_4'


default_args = {
        'start_date': datetime(2021,1,1)
        }

with DAG('parallel_dag', schedule_interval=None, default_args = default_args, catchup=False) as dag:
    task_1 = BashOperator(
            task_id = 'task_1',
            bash_command = "sleep 3"
            )

    with TaskGroup('processing_tasks') as processing_tasks:
        task_2 = PythonOperator(
                task_id = 'task_2',
                python_callable = _task2_fun
                )

        task_3 = PythonOperator(
                task_id = 'task_3',
                python_callable = _task3_fun
                )
    is_condition = BranchPythonOperator(
            task_id = 'is_condition',
            python_callable = _call_function
            )
    
    task_4 = BashOperator(
            task_id = 'task_4',
            bash_command = "sleep 3"
            )

    task_5 = BashOperator(
            task_id = 'task_5',
            bash_command = "sleep 3"
            
            )

    task_6 = BashOperator(
            task_id = 'task_6',
            bash_command = "sleep 3",
            trigger_rule = 'none_failed_or_skipped'
            )

    task_1 >> processing_tasks  >> is_condition >> [task_4, task_5] >> task_6

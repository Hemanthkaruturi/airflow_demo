from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import BranchPythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime
from airflow.utils.task_group import TaskGroup
from airflow.operators.python import PythonOperator
from modes.report_automator import  insert_data_to_sql, execute_sql_script, save_data, delete_table ,export_to_haft
from modes.QC import QC_check


default_args = {
        'start_date': datetime(2021,7,19)
        }

with DAG('autobot', schedule_interval='@daily', default_args = default_args, catchup=False) as dag:
    
    insert_data_to_db = PythonOperator(
            task_id = 'insert_data_to_db',
            python_callable = insert_data_to_sql
            )

    execute_sql_script = PythonOperator(
            task_id = 'execute_sql_script',
            python_callable = execute_sql_script
            )

    save_data = PythonOperator(
            task_id = 'save_data',
            python_callable = save_data
            )
    
    qc_check = BranchPythonOperator(
            task_id = 'qc_check',
            python_callable = QC_check
            )

    send_notification = DummyOperator(
            task_id = 'send_notification',
            trigger_rule = 'none_failed_or_skipped'
            )

    send_qc_failed_alert = DummyOperator(
            task_id = 'send_qc_failed_alert'
            )

    upload_to_haft = DummyOperator(
            task_id = 'upload_to_haft'
            )

    insert_data_to_db >> execute_sql_script >> save_data >> qc_check >> [upload_to_haft, send_qc_failed_alert] >> send_notification

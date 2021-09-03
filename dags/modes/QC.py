import os
import pandas as pd
from datetime import date

today = date.today()
d = today.strftime("%d_%m_%Y")
file_path = f'/home/karuturihemanth/airflow/output_data/Test_output.csv'

files = os.listdir('/home/karuturihemanth/airflow/output_data/')

def QC_check():
    if len(files) != 0:
        df = pd.read_csv(file_path)
        if len(df) != 0:
            return "upload_to_haft"
        else:
            return "send_qc_failed_alert"
    else:
        return "send_qc_failed_alert"


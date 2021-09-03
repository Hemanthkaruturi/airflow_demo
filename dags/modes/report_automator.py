# pip install pypiwin32

import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import os
import re
import yaml

stream = open("/home/karuturihemanth/airflow/config/configure.yml", 'r')
config = yaml.load(stream, Loader=yaml.FullLoader)

host_address = config['Connection'][0]['host_address']
port_number = config['Connection'][1]['port_number']
dbname = config['Connection'][2]['dbname']
usrname = config['Connection'][3]['usrname']
pswd = config['Connection'][4]['pswd']

haft_host = config['Connection'][5]['HAFT'][0]['host']
haft_username = config['Connection'][5]['HAFT'][1]['username']
haft_password = config['Connection'][5]['HAFT'][2]['password']
haft_folder = config['Connection'][5]['HAFT'][3]['folder']

sql_script_execute_cond = config['execute_script'][0]['cond']
params = config['execute_script'][1]['params']
sql_script_path = config['execute_script'][2]['sql_script_path']

output_file_name_cond = config['save_file'][0]['cond']
output_file_name = config['save_file'][1]['output_file_name']

upload_to_pg = config['data_to_greenplum'][0]['upload']
file_type = config['data_to_greenplum'][1]['file_type']
file_sep = config['data_to_greenplum'][2]['sep']
file_sheet_name = config['data_to_greenplum'][3]['sheet_name']
filename = config['data_to_greenplum'][4]['filepath']
table_name = config['data_to_greenplum'][5]['tablename']

delete_output_table = config['delete_output_table']

upload_to_haft = config['upload_to_haft']

exists = 'replace'

def analyize_query(query, d):
    try:
        vars = re.findall(r'(<[a-zA-Z0-9]+>)', query)
        if len(vars) == 0:
            qq = query
        for var in vars:
            q = var.replace('<','').replace('>','')
            query = re.sub('(<{}>)'.format(q), d[q],query)
            qq = query
    except Exception as e:
        qq = query
    return qq

def execute_sql_script(ti):
    if sql_script_execute_cond == 'yes':
        # connect to sql server
        conn = psycopg2.connect(host=host_address, port=port_number, database=dbname, user=usrname, password=pswd)

        # create cursor
        cursor = conn.cursor()

        # get sql statements from the sql script
        fd = open(sql_script_path, 'r')
        ed = open('/home/karuturihemanth/airflow/temp/temp_sql.sql','w+')

        matcher = '/*'[::-1]

        #remove comments from the file
        for line in fd.readlines():
            if line[0:2] != '--' and line[0:2] != '/*' and matcher not in line:
                ed.write(line)

        ed.close()

        fd = open('/home/karuturihemanth/airflow/temp/temp_sql.sql', 'r')
        sqlFile = fd.read()
        fd.close()
        # all SQL commands (split on ';')
        sqlCommands = sqlFile.split(';')
        os.remove('/home/karuturihemanth/airflow/temp/temp_sql.sql')

        queries = []
        # remove \n from commands
        for command in sqlCommands:
            cmd = command.replace('\n',' ').strip()
            if len(cmd) != 0:
                query = analyize_query(cmd, params)
                queries.append(query)
                cursor.execute(query)
        ti.xcom_push(key='queries', value=queries)

def save_data(ti):
    if output_file_name_cond == 'yes':
        # connect to sql server
        conn = psycopg2.connect(host=host_address, port=port_number, database=dbname, user=usrname, password=pswd)
        queries = ti.xcom_pull(key='queries', task_ids=['execute_sql_script'])
        queries = queries[0]
        query = queries[len(queries)-1]
        # save data as csv file
        df = pd.read_sql(query, con=conn)

        df.to_csv(output_file_name, index=False)

def delete_table():
    if delete_output_table:
        # connect to sql server
        conn = psycopg2.connect(host=host_address, port=port_number, database=dbname, user=usrname, password=pswd)
        # create cursor
        cur = conn.cursor()
        queries = ti.xcom_pull(key='queries', task_ids=['execute_sql_script'])
        query = queries[len(queries)-1]
        words = query.split()
        words = [i.lower() for i in words]
        table_ind = words.index('from') + 1
        tablename = words[table_ind]
        cur.execute('drop table if exists {};'.format(tablename))

def insert_data_to_sql():
    if upload_to_pg == 'yes':
        if file_type == 'excel':
            df = pd.read_excel(filename, sheet_name = file_sheet_name)
        else:
            df = pd.read_csv(filename, low_memory=False, sep=file_sep)
        engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(usrname, pswd, host_address,port_number,dbname))
        df.to_sql(table_name, con=engine, index=False, if_exists=exists)

def export_to_haft():
    if upload_to_haft == 'yes':
        conn = pysftp.Connection(haft_host, haft_username=username, haft_password=password)
        conn.cwd(haft_folder)
        conn.put(output_file_name)
        conn.close()

def refresh_excel():
    # xlapp = win32com.client.DispatchEx("Excel.Application")
    # wb = xlapp.Workbooks.Open(filepath)
    # wb.RefreshAll()
    # xlapp.CalculateUntilAsyncQueriesDone()
    # wb.Save()
    # xlapp.Quit()
    pass


import datetime

import airflow
from airflow.operators import bash
from airflow.operators import python
from airflow.providers.http.operators.http import SimpleHttpOperator

YESTERDAY = datetime.datetime.now() - datetime.timedelta(days=1)
default_args = {
    'owner': 'Composer Example Cloud Run-DBT',
    'depends_on_past': False,
    'email': [''],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': datetime.timedelta(minutes=5),
    'start_date': YESTERDAY,
}

with airflow.DAG(
        'composer_http_request_cloud_run',
        'catchup=False',
        default_args=default_args,
        schedule_interval=datetime.timedelta(days=1)) as dag:

    print_token = bash.BashOperator(
        task_id='get_token',
        bash_command='gcloud auth print-access-token'
    )

    token = "{{ task_instance.xcom_pull(task_ids='get_token') }}" # gets output from 'print_token' task

    task_get_op = SimpleHttpOperator(
        task_id='exec_cloud_run_dbt',
        method='POST',
        http_conn_id='cloud_run',
        endpoint='us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/poc-bco-chile/jobs/poc-dbt'
                 '-image:run',
        headers={'Authorization': 'Bearer ' + token },
    )

    def process_data_from_http(**kwargs):
        ti = kwargs['ti']
        http_data = ti.xcom_pull(task_ids='exec_cloud_run_dbt')
        print(http_data)

    process_data = python.PythonOperator(
        task_id='process_data_from_http',
        python_callable=process_data_from_http,
        provide_context=True
    )
    print_token >> task_get_op >> process_data
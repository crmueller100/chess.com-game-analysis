from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.models.param import Param

from datetime import datetime

# from app.test_print import *
# import sys
# sys.path.append('/opt/airflow/app')

# Now you can import the functions from the app module
from get_player_data import get_player_data

def test_print():
    print(f"Hello all")

with DAG(
    dag_id="get_player_games_and_load_data",
    # schedule="0 0 1 * *",
    start_date=datetime(2024, 7, 1),
    schedule_interval="@monthly",
    params={
        "player_username": Param(default="hikaru", type="string", title="Enter in a player's username",)
    },

) as dag:
    t1 = PythonOperator(
    task_id="first_task",
    python_callable=get_player_data,
    op_kwargs={"player": "hikaru"},
    dag=dag

    )
    
    t1
from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.models.param import Param

from datetime import datetime

from get_player_data import get_player_data, get_player_game_archives

def get_player_data_wrapper(player_username):
    get_player_data(player=player_username)

with DAG(
    dag_id="get_player_games_and_load_data",
    start_date=datetime(2024, 7, 1), # maybe make this datetime.utcnow()
    schedule_interval="@monthly",
    params={
        "player_username": Param(default="hikaru", type="string", title="Enter in a player's username")
    },

) as dag:
    t1 = PythonOperator(
        task_id="check_player_exists",
        python_callable=get_player_data,
        op_kwargs={"player": "{{ params.player_username }}"},
        dag=dag
    )
    t1
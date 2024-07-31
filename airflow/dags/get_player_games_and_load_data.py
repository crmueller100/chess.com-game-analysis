from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator
from airflow.models.param import Param

from datetime import datetime

from get_player_data import get_player_data, get_player_game_archives, save_player_game_archives
from connect_to_mongo import connect_to_mongo
from insert_games_into_mongo import insert_games_into_mongo

def save_game_archives_wrapper(player, **kwargs):
    # Retrieve the game archives from XCom
    ti = kwargs['ti']
    game_archives = ti.xcom_pull(task_ids='check_game_archives')
    save_player_game_archives(player, game_archives)


def load_data_to_mongo_wrapper(**kwargs):
    player = kwargs['params']['player_username']
    client, db, collection = connect_to_mongo()
    insert_games_into_mongo(client, db, collection, player)


with DAG(
    dag_id="get_player_games_and_load_data",
    start_date=datetime(2024, 7, 1),  # maybe make this datetime.utcnow()
    schedule_interval="@monthly",
    params={
        "player_username": Param(default="hikaru", type="string", title="Enter in a player's username")
    },
) as dag:
    t1 = PythonOperator(
        task_id="check_player_exists",
        python_callable=get_player_data,
        op_kwargs={"player": "{{ params.player_username }}"},
    )
    t2 = PythonOperator(
        task_id="check_game_archives",
        python_callable=get_player_game_archives,
        op_kwargs={"player": "{{ params.player_username }}"},
        do_xcom_push=True,  # Need to pass the game archives to the next task
    )
    t3 = PythonOperator(
        task_id="save_game_archives",
        python_callable=save_game_archives_wrapper,
        op_kwargs={"player": "{{ params.player_username }}"},
        provide_context=True,  # Allows passing the task instance (ti) to the callable
    )
    t4 = PythonOperator (
        task_id="load_data_to_mongo",
        python_callable=load_data_to_mongo_wrapper,
        params={"player": "{{ params.player_username }}"},
        provide_context=True,
    )

    t1 >> t2 >> t3 >> t4

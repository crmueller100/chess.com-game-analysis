from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator
from airflow.models.param import Param
from datetime import datetime

from get_player_data import get_player_data, get_player_game_archives, save_player_game_archives
from connect_to_mongo import connect_to_mongo
from insert_games_into_mongo import insert_games_into_mongo

def save_game_archives_wrapper(player, **kwargs):
    ti = kwargs['ti']
    game_archives = ti.xcom_pull(task_ids=f'check_game_archives_{player}')
    save_player_game_archives(player, game_archives)


def load_data_to_mongo_wrapper(player, **kwargs):
    client, db, collection = connect_to_mongo()
    insert_games_into_mongo(client, db, collection, player)


with DAG(
    dag_id="get_player_games_and_load_data",
    start_date=datetime(2024, 1, 1),  # Use a fixed start date
    schedule_interval="@monthly",
    params={
        "player_usernames": Param(default=['hikaru', 'cmuell'], type="array", title="Enter player usernames. Separate each name with a newline."),
    },
) as dag:
    players = dag.params["player_usernames"]  # Resolve params to a Python list
    for player in players:
        sanitized_player = player.strip()  # Sanitize player names for valid task IDs
        t1 = PythonOperator(
            task_id=f"check_player_exists_{sanitized_player}",
            python_callable=get_player_data,
            op_kwargs={"player": sanitized_player},  # Pass the individual player
        )
        t2 = PythonOperator(
            task_id=f"check_game_archives_{sanitized_player}",
            python_callable=get_player_game_archives,
            op_kwargs={"player": sanitized_player},  # Pass the individual player
            do_xcom_push=True,
        )
        t3 = PythonOperator(
            task_id=f"save_game_archives_{sanitized_player}",
            python_callable=save_game_archives_wrapper,
            op_kwargs={"player": sanitized_player},  # Pass the individual player
            provide_context=True,
        )
        t4 = PythonOperator(
            task_id=f"load_data_to_mongo_{sanitized_player}",
            python_callable=load_data_to_mongo_wrapper,
            op_kwargs={"player": sanitized_player},  # Pass the individual player
        )

        t1 >> t2 >> t3 >> t4

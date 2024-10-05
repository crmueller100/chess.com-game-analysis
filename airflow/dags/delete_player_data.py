from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator
from airflow.models.param import Param

from datetime import datetime
import asyncio

from get_player_data import get_player_data
from connect_to_mongo import connect_to_mongo

def delete_player_data(player):
    client, db, collection = connect_to_mongo()
    result = collection.delete_many({"player": player})
    print(f"Deleted {result.deleted_count} games for {player}")


with DAG(
    dag_id="delete_player_data",
    schedule_interval=None,  # This DAG will be triggered manually, not on a schedule
    params={
        "player_username": Param(default="<enter_player_username>", type="string", title="Enter in a player's username"),
    },
) as dag:
    t1 = PythonOperator(
        task_id="check_player_exists",
        python_callable=get_player_data,
        op_kwargs={"player": "{{ params.player_username }}"},
    ),
    t2 = PythonOperator(
        task_id="delete_player_data",
        python_callable=delete_player_data,
        op_kwargs={"player": "{{ params.player_username }}"}
    )

    t1 >> t2
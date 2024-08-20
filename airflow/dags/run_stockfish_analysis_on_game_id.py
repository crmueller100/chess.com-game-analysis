from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator
from airflow.models.param import Param

from datetime import datetime
import asyncio

from stockfish_analysis import analyze_wdl_with_stockfish

def analyze_wdl_wrapper(**kwargs):
    """
    Wrapper function to execute the async analyze_wdl_with_stockfish function.
    """
    game_id = kwargs["params"]["game_id"]
    result = asyncio.run(analyze_wdl_with_stockfish(game_id))  # Await the coroutine
    return result


with DAG(
    dag_id="run_stockfish_analysis_on_game_id",
    start_date=datetime.now(),
    schedule_interval=None,  # This DAG will be triggered manually, not on a schedule
    params={
        "game_id": Param(default=None, type="string", title="Enter in a game ID")
    },
) as dag:
    t1 = PythonOperator(
        task_id="call_stockfish_analysis",
        python_callable=analyze_wdl_wrapper,
        op_kwargs={"game_id": "{{ params.game_id }}"},
    )

    t1

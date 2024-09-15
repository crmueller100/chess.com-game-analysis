from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator
from airflow.models.param import Param

from datetime import datetime
import asyncio

from stockfish_analysis import analyze_wdl_with_stockfish, analyze_wdl_with_stockfish_last_n_games

def analyze_wdl_wrapper(**kwargs):
    """
    Wrapper function to execute the async analyze_wdl_with_stockfish function.
    """
    print(f'running analyze_wdl_wrapper with kwaregs: {kwargs}')
    player = kwargs["params"]["player_username"]
    num_games = kwargs["params"]["num_games"]
    asyncio.run(analyze_wdl_with_stockfish_last_n_games(player, num_games))


with DAG(
    dag_id="run_stockfish_analysis_on_last_n_games",
    start_date=datetime.now(),
    schedule_interval=None,  # This DAG will be triggered manually, not on a schedule
    params={
        "player_username": Param(default="hikaru", type="string", title="Enter in a player's username"),
        "num_games": Param(default=None, type="integer", maximum=10, title="Enter the number of games to analyze. Maximum of 10 games per run")
    },
) as dag:
    print('this is the dAGs')
    t1 = PythonOperator(
        task_id="call_stockfish_analysis",
        python_callable=analyze_wdl_wrapper
    )

    t1

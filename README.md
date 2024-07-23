# chess.com-game-analysis
### Goal
Improve my chess game by analyzing performance using Chess.com's [Public API](https://www.chess.com/news/view/published-data-api).


### Info
By searching for a Chess.com username, this program queries information about their games, openings, positions, wins vs. losses, and overall performance. It compiles it into a dashboard and allows the user to see areas for needed for improvement.

### Tools
Python and MongoDB running in a Docker container. (More coming soon!) 

### Usage
The players' data will be saved to the `data/` directory using the directory name `data/game_archives/<player_username>/<year>_<month>`. The `data/` directory is also where the volumes for the database services are mounted.

### Setup

Build the docker images and start the mongo and app services. Remember to run `--build` when you add a new line to the `requirements.txt` file:
```
docker-compose up [--build] -d
```

If you want to enter the app container to test/run some code, use this:
```
docker exec -it <python container_id> bash
```
Then you can simply run `python app/main.py`

You should set `AIRFLOW_UID`. Otherwise, the files created in `airflow/` will be created with `root` use owndership. Configure the user by running this:
```
echo -e "AIRFLOW_UID=$(id -u)" > .env
```

Now, you need to run db migrations and create the first user account. You only need to run this once:
```
docker compose up airflow-init
```

# chess.com-game-analysis
# Goal
Improve my chess rating by leveraging Chess.com's [Public API](https://www.chess.com/news/view/published-data-api) to build a data pipeline and analyze game performance.

# Overview
By searching for a Chess.com username, this program queries information about players' games, openings, positions, wins vs. losses, and overall performance. It compiles this information into a dashboard and allows the user to see areas for needed for improvement.

### Tools
This app is written primarily in Python. Chess data is stored in a MongoDB instance. There is an Airflow instance running that provides a UI for users to easily manipulate data and facilitate deeper analysis. The dashboard was created using [Streamlit](https://streamlit.io/). Most of the MongoDB logic is written using `pymongo`. The entire app exists within a Docker container.

### Usage
The players' data will be saved to the `data/` directory using the directory name `data/game_archives/<player_username>/<year>_<month>`. The `data/` directory is also where the volumes for the database services are mounted.

# Setup

### Configure Docker and Environment
It's bad practice to use the default values for usernames/passwords that are defined in `docker-compose.yml`. Create a `.env` file in the root directory and fill in new values for these credentials. Otherwise, docker will use the default values.
```
AIRFLOW_UID=501
_AIRFLOW_WWW_USER_USERNAME=
_AIRFLOW_WWW_USER_PASSWORD=

MONGO_HOST=my-mongodb
MONGO_PORT=27017
MONGO_INITDB_ROOT_USERNAME=
MONGO_INITDB_ROOT_PASSWORD=

POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
```


### Run Docker
Build the docker images and start the mongo and app services. Remember to run `--build` if you add a new line to the `requirements.txt` file:
```
docker compose up [--build] -d
```

If you want to enter the app container to test/run some code, use this:
```
docker exec -it <python_container_id> bash
```
Then you can simply run `python main.py`

If you're running this app on a Linux machine, you need to set `AIRFLOW_UID`. Otherwise, the files created in `airflow/` will be created with `root` use ownership. If you're not on Linux, you'll get a warning that can be ignored. Configure the user by running this:
```
echo -e "AIRFLOW_UID=$(id -u)" > .env
```

Now, you need to run db migrations and create the first user account. You only need to run this once:
```
docker compose up airflow-init
```

### Initialize Mongo DB
Once inside the `app` docker service, you'll need to initialize MongoDB. This only needs to be done once. Run the following command:
```
python mongo_init.py
```

### Stockfish
[Stockish](https://stockfishchess.org/) is the accepted chess engine within the community. You will need to download the binaries [here](https://stockfishchess.org/download/) in order to use it for deep analysis. Once you open the file, note the file location. It will need to be entered under `STOCKFISH_PATH` in the `docker-compose.yml` file. I placed it in the `stockfish/` directory at the root level. The path is to the *executable*, so you'll need to do something like `STOCKFISH_PATH = "stockfish/stockfish-macos-m1-apple-silicon"`. Running this on a MacOS, I needed to use the ARM binaries [here](https://stockfishchess.org/download/arm/) (due to Docker creating a Linux environment).

### Opening Analysis
Chess.com returns games as a PGN (portable game notation) format. The codes that represent each opening identified in the PGN were mapped using [ECO mappings](https://www.365chess.com/eco.php). 



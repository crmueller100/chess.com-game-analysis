# chess.com Game Analysis App
# Goal
Improve my chess rating by leveraging Chess.com's [Public API](https://www.chess.com/news/view/published-data-api) to build a data pipeline and analyze game performance.

# Overview
This application uses chess.com's public API for to query data about players' games, openings, positions, wins vs. losses, and overall performance. This information is compiled into an interactive dashboard where users can:
*   Visualize their rating trends
*   Analyze their opening choices
*   Identify blunders and mistakes using Stockfish

# Quick Start
1. Download the [stockfish binaries](https://stockfishchess.org/download/) and drop the folder in the root directory with the name `stockfish/`
2. Update the value of `STOCKFISH_PATH` in the `.env` file. (The ARM/Android download works within the Docker architecture)
3. Create a `.env` file and fill in the RHS of these variables
    ```
    STOCKFISH_PATH=/usr/local/bin/stockfish/stockfish-android-armv8

    AIRFLOW_UID=501 
    _AIRFLOW_WWW_USER_USERNAME=
    _AIRFLOW_WWW_USER_PASSWORD=

    MONGO_HOST=
    MONGO_PORT=27017
    MONGO_INITDB_ROOT_USERNAME=
    MONGO_INITDB_ROOT_PASSWORD=

    POSTGRES_USER=
    POSTGRES_PASSWORD=
    POSTGRES_DB=
    ```
4. Run `docker compose up airflow-init`
5. Run `docker compose up --build -d`
6. Run `docker ps` and copy the ID of the `app` container
7. Enter the `app` container by running `docker exec -it <container_id> bash`
8. Once in the `app` container, initialize MongoDB by running `python mongo_init.py`

With the setup complete, you can:
* Explore the dashboard by going to http://localhost:8501/
* Trigger jobs through the Airflow UI by going to http://localhost:8080/
* Run custom functions within the `app` container by running `python <some_file.py>


# Technical Documentation
### Tools
This app is written primarily in Python. The game data is stored in a MongoDB instance. The Airflow webserver provides a UI for users to easily manipulate/manage the data and trigger jobs that facilitate deeper analysis. The dashboard was created using [Streamlit](https://streamlit.io/). Most of the MongoDB logic is written using `pymongo`. The entire application is containerized using Docker for easy deployment.

### Usage
The players' game data will be saved to the `data/` directory under the directory name `data/game_archives/<player_username>/<year>_<month>`. The `data/` directory is also where the volumes for the database services are mounted. `data/mongo_data/` and `data/postgres-db-volume/` will be created automatically when the Docker image is built.

# Setup

### Stockfish
[Stockish](https://stockfishchess.org/) is the accepted chess engine within the chess community. You will need to download the binaries [here](https://stockfishchess.org/download/) in order to use it for deep analysis. Place the binaries in the `stockfish/` directory at the root level. You will need to enter the path under the `STOCKFISH_PATH` variable in the `.env` file. Running this on a MacOS, I needed to use the ARM binaries [here](https://stockfishchess.org/download/arm/) (due to Docker creating a Linux environment).

### Configure Docker and Environment
It's bad practice to use the default values for usernames/passwords that are defined in `docker-compose.yml`. Instead, create a `.env` file in the root directory and fill in new values for these credentials.
```
STOCKFISH_PATH=/usr/local/bin/stockfish/stockfish-android-armv8

AIRFLOW_UID=501
_AIRFLOW_WWW_USER_USERNAME=
_AIRFLOW_WWW_USER_PASSWORD=

MONGO_HOST=
MONGO_PORT=27017
MONGO_INITDB_ROOT_USERNAME=
MONGO_INITDB_ROOT_PASSWORD=

POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
```


### Run Docker
If you're running this app on a Linux machine, you need to set `AIRFLOW_UID`. Otherwise, the files created in `airflow/` will be created with `root` user ownership. If you're not on Linux, you'll get a warning that can be ignored. Configure the user by running this (or just enter it manually in the `.env` file):
```
echo -e "AIRFLOW_UID=$(id -u)" > .env
```

Now, you need to run db migrations and create the first user account. You only need to run this once:
```
docker compose up airflow-init
```

Build the Docker images and start the mongo and app services. Remember to run `--build` if you are building this container for the first time or you add a new line to the `requirements.txt` file:
```
docker compose up [--build] -d
```

If you want to enter the `app` container to run specific files and functions, use this:
```
docker exec -it <python_container_id> bash
```
Then you can simply run `python main.py`

### Initialize Mongo DB
Once inside the `app` container, you'll need to initialize MongoDB. This only needs to be done once. Run the following command:
```
python mongo_init.py
```

### Opening Analysis
Chess.com returns games as a PGN (portable game notation) format. The codes that represent each opening identified in the PGN were mapped using [ECO mappings](https://www.365chess.com/eco.php). 

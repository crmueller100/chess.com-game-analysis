# chess.com-game-analysis
### Goal
Improve my chess game by analyzing performance using Chess.com's [Public API](https://www.chess.com/news/view/published-data-api).


### Info
By searching for a Chess.com username, this program queries information about their games, openings, positions, wins vs. losses, and overall performance. It compiles it into a dashboard and allows the user to see areas for needed for improvement.

### Setup
Build and run Docker image with (this uses the Flask way)
```
docker build -t chess-analysis .
docker run -it chess-analysis
```

### Usage
The players' data will be saved to the `data/` directory using the directory name `data/game_archives/<player_username>/<year>_<month>`.

Build the docker images and start the mongo and app services. Need to run `--build` when you add a new line to the `requirements.txt` file:
```
docker-compose up --build
docker-compose up -d
```

If you want to enter the app container to test/run some code, use this:
```
docker exec -it <python container_id> bash
```

Then you can simply run `python src/<somefile>.py`


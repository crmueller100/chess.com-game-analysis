# chess.com-game-analysis
### Goal
Improve my chess game by analyzing performance using Chess.com's [Public API](https://www.chess.com/news/view/published-data-api).


### Info
By searching for a Chess.com username, this program queries information about their games, openings, positions, wins vs. losses, and overall performance. It compiles it into a dashboard and allows the user to see areas for needed for improvement.

### Setup
Build and run Docker image with
```
docker build -t chess-analysis .
docker run -it chess-analysis
```

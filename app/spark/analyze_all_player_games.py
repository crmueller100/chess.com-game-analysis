from pyspark.sql import SparkSession

# Create a Spark session
spark = SparkSession.builder \
    .appName("HelloSpark") \
    .getOrCreate()

# Create a simple data frame
data = [("Hello", "World"), ("PySpark", "Test")]
columns = ["Column1", "Column2"]

df = spark.createDataFrame(data, columns)

# Show the data frame content
df.show()

# Stop the Spark session
spark.stop()

# from insert_games_into_mongo import insert_games_into_mongo

# from pyspark.sql import SparkSession



# spark = SparkSession.builder.appName("ChessAnalysis").getOrCreate()
    # .config("spark.mongodb.input.uri", "mongodb://localhost:27017/chess_db.games") \
    # .config("spark.mongodb.output.uri", "mongodb://localhost:27017/chess_db.games") \
    

# Load chess games collection from MongoDB
# games_df = spark.read.format("mongo").load()

# # Filter games where there was a winner
# games_with_winner = games_df.filter((col("winner") == "white") | (col("winner") == "black"))

# # Add a column to denote if a given player was the winner
# player = "your_player_username"
# games_with_winner = games_with_winner.withColumn(
#     "player_won",
#     when((col("white.username") == player) & (col("winner") == "white"), 1)
#     .when((col("black.username") == player) & (col("winner") == "black"), 1)
#     .otherwise(0)
# )

# # Calculate win rate for the player
# win_rate = games_with_winner.groupBy("player_won").count()
# win_rate.show()

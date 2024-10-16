from connect_to_mongo import connect_to_mongo
    
from pyspark.sql import SparkSession


client, db, collection = connect_to_mongo()

# Update with your database and collection
mongo_uri = "mongodb://<username>:<password>@<mongo_host>:27017/chess_data"

spark = SparkSession.builder \
    .appName("AllPlayerAnalysis") \
    .config("spark.mongodb.read.connection.uri", mongo_uri) \
    .config("spark.mongodb.read.collection", "games") \
    .getOrCreate()

# Now try reading from MongoDB
df = spark.read.format("mongodb").load()

df.show()

spark.stop()
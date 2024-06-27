import os
import pymongo

# Define MongoDB connection parameters
username = "root"
password = "example"
host = os.getenv("MONGO_HOST")
port = os.getenv("MONGO_PORT")

# Create the connection string with authSource
connection_string = f"mongodb://{username}:{password}@{host}:{port}"

# Establish connection to MongoDB
client = pymongo.MongoClient(connection_string)
db = client["chess_data"]
collection = db["games"]

# Insert a document into the collection
game1 = {"url": "https://www.chess.com/game/live/692667823"}
collection.insert_one(game1)

print(client.list_database_names())

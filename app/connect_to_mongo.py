import os
import pymongo

from pymongo.errors import ConnectionFailure, OperationFailure, ConfigurationError

def connect_to_mongo():
    print(f"Connecting to MongoDB")
    try:
        # Define MongoDB connection parameters
        username = os.environ.get("MONGO_INITDB_ROOT_USERNAME")
        password = os.environ.get("MONGO_INITDB_ROOT_PASSWORD")
        host = os.environ.get("MONGO_HOST")
        port = os.environ.get("MONGO_PORT")

        connection_string = f"mongodb://{username}:{password}@{host}:{port}"

        # Establish connection to MongoDB
        client = pymongo.MongoClient(connection_string)
        db = client["chess_data"]
        collection = db["games"]

        return client, db, collection 

    except ConnectionFailure as e:
        print(f"Could not connect to MongoDB: {e}")
        return None, None, None

    except OperationFailure as e:
        print(f"MongoDB operation failed: {e}")
        return None, None, None
    
    except ConfigurationError as e:
        print(f"MongoDB configuration error: {e}")
        return None, None, None


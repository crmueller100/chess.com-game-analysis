import os
import pymongo

from pymongo.errors import ConnectionFailure, OperationFailure, ConfigurationError

def connect_to_mongo():
    environment = os.environ.get("ENVIRONMENT", "local")
    print(f"Connecting to MongoDB in {environment} environment")

    try:
        if environment == "local":
            username = os.environ.get("MONGO_INITDB_ROOT_USERNAME")
            password = os.environ.get("MONGO_INITDB_ROOT_PASSWORD")
            host = os.environ.get("MONGO_HOST")
            port = os.environ.get("MONGO_PORT")

            connection_string = f"mongodb://{username}:{password}@{host}:{port}"

        elif environment == "cloud":
            username = os.environ.get("DOCDB_USERNAME")
            password = os.environ.get("DOCDB_PASSWORD")
            host = os.environ.get("DOCDB_HOST")
            port = os.environ.get("DOCDB_PORT", "27017")  # Default port for DocumentDB
            tls = os.environ.get("DOCDB_TLS", "true")
    
            ssl_cert_path = os.environ.get("SSL_CERT_PATH", "/usr/local/share/ca-certificates/global-bundle.pem")

            # Enable TLS/SSL for DocumentDB
            connection_string = f"mongodb://{username}:{password}@{host}:{port}/?tls={tls}&tlsCAFile={ssl_cert_path}"


        else:
            raise ValueError("Invalid ENVIRONMENT value. Use 'local' or 'cloud'.")

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


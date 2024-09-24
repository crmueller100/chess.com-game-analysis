from connect_to_mongo import connect_to_mongo

def mongo_init():
    client, db, collection  = connect_to_mongo()

    # create an index on the 'player' field
    print('Creating index on player field')
    collection.create_index('player', unique=False)

if __name__ == "__main__":
    print('Running mongo-init')
    mongo_init()
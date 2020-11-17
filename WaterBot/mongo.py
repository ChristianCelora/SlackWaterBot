import os 
import pymongo
import mongomock

class MongoConnector:
    #dbname = os.environ.get('MONGO_DBNAME')
    #psw = os.environ.get('MONGO_PSW')
    #user = os.environ.get('MONGO_USER')
    #conn_str = .format(user, psw, dbname)
    client = pymongo.MongoClient(
        "mongodb+srv://{}:{}@waterbot.xkmvw.mongodb.net/{}?retryWrites=true&w=majority".format(
            os.environ.get('MONGO_USER'), os.environ.get('MONGO_PSW'), os.environ.get('MONGO_DBNAME')
        )
    )
    db = client.WaterBot

    @staticmethod
    def getInstance():
        return MongoConnector.db

class MockMongoManager():
    mock_db = mongomock.MongoClient().WaterBot
    #mock_collection = mongomock.MongoClient().WaterBot.collection

    @staticmethod
    def getInstance():
        return MockMongoManager.mock_db
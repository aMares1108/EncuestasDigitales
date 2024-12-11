from pymongo import MongoClient
from os import getenv
from bson import ObjectId

def get_forms(user_id: ObjectId | None = None, start: int = 0, limit: int = 0):
    with MongoClient(getenv('MONGO_URI')) as mongo:
        if user_id:
            res = mongo.test.form.find({'user':user_id}).skip(start).limit(limit).to_list()
        else:
            res = mongo.test.form.find().skip(start).limit(limit).to_list()
    return res
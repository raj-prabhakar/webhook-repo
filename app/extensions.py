from flask_pymongo import PyMongo
from datetime import datetime
import pytz

mongo = PyMongo()

def create_event(request_id, author, action, from_branch, to_branch, timestamp):
    return {
        "request_id": request_id,
        "author": author,
        "action": action,
        "from_branch": from_branch,
        "to_branch": to_branch,
        "timestamp": timestamp,
        "created_at": datetime.now(pytz.UTC)
    }

def setup_mongodb_indexes():
    mongo.db.events.create_index("request_id", unique=True)  
    mongo.db.events.create_index("action")                
    mongo.db.events.create_index("timestamp")              

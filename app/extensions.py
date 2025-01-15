from flask_pymongo import PyMongo
from datetime import datetime
import pytz

# Initialize PyMongo for MongoDB integration with Flask
mongo = PyMongo()

def create_event(request_id, author, action, from_branch, to_branch, timestamp):
    """
    Create a dictionary representing an event.

    Args:
        request_id (str): Unique identifier for the event request.
        author (str): Name of the author who performed the action.
        action (str): The type of action (e.g., "PUSH", "PULL_REQUEST", "MERGE").
        from_branch (str): Source branch (used for pull requests or merges).
        to_branch (str): Target branch.
        timestamp (datetime): The timestamp when the action occurred.

    Returns:
        dict: A dictionary containing event details, including the creation timestamp.
    """
    return {
        "request_id": request_id,               # Unique identifier to ensure no duplicate events
        "author": author,                       # Author who performed the action
        "action": action,                       # Action type (e.g., PUSH, PULL_REQUEST, MERGE)
        "from_branch": from_branch,             # Source branch for the action
        "to_branch": to_branch,                 # Target branch for the action
        "timestamp": timestamp,                 # Timestamp of the action
        "created_at": datetime.now(pytz.UTC)    # Current timestamp in UTC, for record creation
    }

def setup_mongodb_indexes():
    """
    Set up indexes in the MongoDB collection for efficient querying.

    Indexes are created for:
    - request_id: Ensures unique request IDs to avoid duplicate records.
    - action: Optimizes querying by action types (e.g., PUSH, PULL_REQUEST, MERGE).
    - timestamp: Enables efficient retrieval of records based on time.
    """
    # Create a unique index on 'request_id' to ensure no duplicate events with the same ID
    mongo.db.events.create_index("request_id", unique=True)

    # Create an index on 'action' to improve search performance by action type
    mongo.db.events.create_index("action")

    # Create an index on 'timestamp' to optimize queries based on time
    mongo.db.events.create_index("timestamp")

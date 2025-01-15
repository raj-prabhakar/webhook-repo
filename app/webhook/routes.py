from flask import Blueprint, request, jsonify, current_app
from ..extensions import mongo, create_event
from bson import ObjectId
from datetime import datetime
import pytz

# Create a Flask Blueprint for handling webhook routes
webhook = Blueprint('Webhook', __name__)

# Helper function to serialize ObjectId to string
def serialize_objectid(data):
    """
    Recursively converts ObjectId fields in data to strings to ensure JSON compatibility.
    Works for dictionaries, lists, and ObjectId instances.
    """
    if isinstance(data, ObjectId):
        return str(data)
    elif isinstance(data, dict):
        return {key: serialize_objectid(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [serialize_objectid(item) for item in data]
    return data

# Route to handle webhook events from GitHub
@webhook.route('/receiver', methods=["POST"])
def handle_receiver():
    """
    Handles incoming webhook events from GitHub.
    Stores events related to pull requests and push actions in the database.
    """
    print("Received webhook event")
    if request.headers['Content-Type'] == 'application/json':
        try:
            # Parse the JSON payload
            payload = request.json
            # Extract the event type from headers
            event_type = request.headers.get('X-GitHub-Event', '').upper()

            print(f"Event Type: {event_type}")  # Log the event type for debugging

            # Handle pull request events
            if event_type == 'PULL_REQUEST':
                # Check if the pull request was merged
                is_merged = payload['action'] == 'closed' and payload['pull_request']['merged'] == True

                if is_merged:
                    # Create an event record for the merge
                    event_data = create_event(
                        request_id=str(payload['pull_request']['id']),
                        author=payload['pull_request']['user']['login'],
                        action="MERGE",
                        from_branch=payload['pull_request']['head']['ref'],
                        to_branch=payload['pull_request']['base']['ref'],
                        timestamp=datetime.now(pytz.UTC)
                    )
                    
                    # Insert the event record into the database
                    inserted = current_app.mongo.db.events.insert_one(event_data)
                    event_data['_id'] = str(inserted.inserted_id)

                    return jsonify({
                        'status': 'success',
                        'message': 'Merge event stored successfully',
                        'data': event_data
                    }), 200
                
                elif payload['action'] == 'opened':
                    # Create an event record for the pull request
                    event_data = create_event(
                        request_id=str(payload['pull_request']['id']),
                        author=payload['pull_request']['user']['login'],
                        action="PULL_REQUEST",
                        from_branch=payload['pull_request']['head']['ref'],
                        to_branch=payload['pull_request']['base']['ref'],
                        timestamp=datetime.now(pytz.UTC)
                    )
                    
                    # Insert the event record into the database
                    inserted = current_app.mongo.db.events.insert_one(event_data)
                    event_data['_id'] = str(inserted.inserted_id)

                    return jsonify({
                        'status': 'success',
                        'message': 'Pull request event stored successfully',
                        'data': event_data
                    }), 200

            # Handle push events
            elif event_type == 'PUSH':
                # Ignore merge commits in push events
                if not any('Merge pull request' in commit.get('message', '') 
                          for commit in payload.get('commits', [])):
                    # Determine the from_branch if the push isn't a new branch
                    from_branch = payload['before'] if payload['before'] != "0000000000000000000000000000000000000000" else None

                    # Create an event record for the push
                    event_data = create_event(
                        request_id=payload['after'],
                        author=payload['pusher']['name'],
                        action="PUSH",
                        from_branch=from_branch,
                        to_branch=payload['ref'].split('/')[-1],
                        timestamp=datetime.now(pytz.UTC)
                    )
                    
                    # Insert the event record into the database
                    inserted = current_app.mongo.db.events.insert_one(event_data)
                    event_data['_id'] = str(inserted.inserted_id)

                    return jsonify({
                        'status': 'success',
                        'message': 'Push event stored successfully',
                        'data': event_data
                    }), 200

            # Default response for unhandled event types
            return jsonify({'status': 'success', 'message': 'Event processed but not stored'}), 200

        except Exception as e:
            # Log and return an error response if an exception occurs
            print(f"Error in handle_receiver: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

# Route to fetch all stored events from the database
@webhook.route('/fetch_events', methods=["GET"])
def fetch_events():
    """
    Fetches and returns all stored webhook events from the database.
    """
    try:
        # Retrieve events from the database, sorted by creation date in descending order
        events = list(current_app.mongo.db.events.find().sort("created_at", -1))

        # Serialize ObjectId fields to strings for JSON compatibility
        events = serialize_objectid(events)

        if events:
            return jsonify({
                'status': 'success',
                'message': 'Fetched events successfully',
                'data': events
            }), 200
        else:
            return jsonify({
                'status': 'success',
                'message': 'No events found'
            }), 200
    except Exception as e:
        # Return an error response if an exception occurs
        return jsonify({
            'status': 'error',
            'message': f"Error fetching events: {str(e)}"
        }), 500

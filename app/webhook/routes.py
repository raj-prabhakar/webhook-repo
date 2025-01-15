from flask import Blueprint, request, jsonify, current_app
from ..extensions import mongo, create_event
from bson import ObjectId
from datetime import datetime
import pytz

webhook = Blueprint('Webhook', __name__)

# Helper function to convert ObjectId to string
def serialize_objectid(data):
    if isinstance(data, ObjectId):
        return str(data)
    elif isinstance(data, dict):
        return {key: serialize_objectid(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [serialize_objectid(item) for item in data]
    return data

@webhook.route('/receiver', methods=["POST"])
def handle_receiver():
    print("Received webhook event")
    if request.headers['Content-Type'] == 'application/json':
        try:
            payload = request.json
            event_type = request.headers.get('X-GitHub-Event', '').upper()

            print(f"Event Type: {event_type}")  

            if event_type == 'PULL_REQUEST':
                is_merged = payload['action'] == 'closed' and payload['pull_request']['merged'] == True

                if is_merged:
                    event_data = create_event(
                        request_id=str(payload['pull_request']['id']),
                        author=payload['pull_request']['user']['login'],
                        action="MERGE",
                        from_branch=payload['pull_request']['head']['ref'],
                        to_branch=payload['pull_request']['base']['ref'],
                        timestamp=datetime.now(pytz.UTC)
                    )
                    
                    inserted = current_app.mongo.db.events.insert_one(event_data)
                    event_data['_id'] = str(inserted.inserted_id)

                    return jsonify({
                        'status': 'success',
                        'message': 'Merge event stored successfully',
                        'data': event_data
                    }), 200
                
                elif payload['action'] == 'opened':
                    event_data = create_event(
                        request_id=str(payload['pull_request']['id']),
                        author=payload['pull_request']['user']['login'],
                        action="PULL_REQUEST",
                        from_branch=payload['pull_request']['head']['ref'],
                        to_branch=payload['pull_request']['base']['ref'],
                        timestamp=datetime.now(pytz.UTC)
                    )
                    
                    inserted = current_app.mongo.db.events.insert_one(event_data)
                    event_data['_id'] = str(inserted.inserted_id)

                    return jsonify({
                        'status': 'success',
                        'message': 'Pull request event stored successfully',
                        'data': event_data
                    }), 200

            elif event_type == 'PUSH':
                if not any('Merge pull request' in commit.get('message', '') 
                          for commit in payload.get('commits', [])):
                    from_branch = payload['before'] if payload['before'] != "0000000000000000000000000000000000000000" else None

                    event_data = create_event(
                        request_id=payload['after'],
                        author=payload['pusher']['name'],
                        action="PUSH",
                        from_branch=from_branch,
                        to_branch=payload['ref'].split('/')[-1],
                        timestamp=datetime.now(pytz.UTC)
                    )
                    
                    inserted = current_app.mongo.db.events.insert_one(event_data)
                    event_data['_id'] = str(inserted.inserted_id)

                    return jsonify({
                        'status': 'success',
                        'message': 'Push event stored successfully',
                        'data': event_data
                    }), 200

            return jsonify({'status': 'success', 'message': 'Event processed but not stored'}), 200

        except Exception as e:
            print(f"Error in handle_receiver: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500


@webhook.route('/fetch_events', methods=["GET"])
def fetch_events():
    try:
        events = list(current_app.mongo.db.events.find().sort("created_at", -1))

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
        return jsonify({
            'status': 'error',
            'message': f"Error fetching events: {str(e)}"
        }), 500

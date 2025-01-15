# GitHub Webhook Handler

A Flask-based application that handles GitHub webhooks to track repository events like pull requests and pushes. The application stores these events in a MongoDB database and provides endpoints to retrieve the event history.

## Features

- Receives and processes GitHub webhook events
- Handles Pull Request events (opening and merging)
- Handles Push events (excluding merge commits)
- Stores event data in MongoDB
- Provides an API endpoint to fetch event history
- Automatically captures event metadata including timestamps and author information

## Prerequisites

- Python 3.x
- MongoDB
- Flask
- PyMongo
- pytz

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Configure MongoDB connection in your Flask application:

```python
app.config["MONGO_URI"] = "mongodb://localhost:27017/your_database"
```

## API Endpoints

### Webhook Receiver
- **URL**: `http://127.0.0.1:5000/webhook/receiver`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Description**: Receives webhook events from GitHub
- **Handled Events**:
  - Pull Request events (opening and merging)
  - Push events (excluding merge commits)
- **Success Response**:
  ```json
  {
    "status": "success",
    "message": "Event stored successfully",
    "data": {
      "request_id": "...",
      "author": "...",
      "action": "...",
      "from_branch": "...",
      "to_branch": "...",
      "timestamp": "..."
    }
  }
  ```

### Fetch Events
- **URL**: `http://127.0.0.1:5000/webhook/fetch_events`
- **Method**: `GET`
- **Description**: Retrieves all stored webhook events
- **Success Response**:
  ```json
  {
    "status": "success",
    "message": "Fetched events successfully",
    "data": [
      {
        // Event objects
      }
    ]
  }
  ```

## Event Types

### Pull Request Events
The application tracks two types of pull request events:
- Opening a new pull request (`PULL_REQUEST`)
- Merging a pull request (`MERGE`)

### Push Events
Push events are tracked with the following information:
- Commit hash
- Author information
- Source and target branches
- Timestamp

Note: Merge commits in push events are ignored to avoid duplicate entries with pull request merges.

## Development

To run the application in development mode:

```bash
python run.py
```

## Setting Up GitHub Webhooks

1. Go to your GitHub repository settings
2. Navigate to Webhooks
3. Add a new webhook:
   - Payload URL: `http://your-domain/receiver`
   - Content type: `application/json`
   - Select events: Pull requests and Pushes

## Deployment on AWS
Due to the constraint in the problem statement of using gunicorn as a production server I have performed the deployment of this repository on an AWS EC2 machine as gunicorn couldn't work on my window based machine. The webhook receiver endpoint of the github dummy repo 'action-repo' is also set in the url of the deployed code. 

Deployment link: http://50.17.89.168:5000/

from flask import Flask, render_template
from flask_pymongo import PyMongo
from app.webhook.routes import webhook
import os
from dotenv import load_dotenv

def create_app():
    """
    Factory function to create and configure the Flask application.
    Sets up MongoDB connection, loads environment variables, 
    and registers the webhook blueprint.
    """
    
    # Load environment variables from a .env file
    load_dotenv()
    
    # Initialize the Flask application
    app = Flask(__name__)
    
    # Configure MongoDB URI from environment variables
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")

    # Initialize PyMongo with the Flask application
    mongo = PyMongo(app)

    # Attach the MongoDB client to the app instance for easy access
    app.mongo = mongo

    # Test MongoDB connection
    try:
        mongo.db.command('ping')  # Command to check if MongoDB is reachable
        print("MongoDB connection successful!")
    except Exception as e:
        # Log the error and raise it to stop app initialization if the connection fails
        print(f"MongoDB connection error: {str(e)}")
        raise e

    # Register the webhook blueprint with a URL prefix
    app.register_blueprint(webhook, url_prefix='/webhook')

    # Define the root route
    @app.route('/')
    def home():
        """
        Serves the homepage.
        Renders the 'home.html' template.
        """
        return render_template('home.html')

    # Return the configured Flask application instance
    return app

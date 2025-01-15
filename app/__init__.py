from flask import Flask, render_template
from flask_pymongo import PyMongo
from app.webhook.routes import webhook
import os
from dotenv import load_dotenv

def create_app():
    
    load_dotenv()
    app = Flask(__name__)
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")

    mongo = PyMongo(app)

    app.mongo = mongo

    try:
        mongo.db.command('ping') 
        print("MongoDB connection successful!")
    except Exception as e:
        print(f"MongoDB connection error: {str(e)}")
        raise e

    app.register_blueprint(webhook, url_prefix='/webhook')

    @app.route('/')
    def home():
        return render_template('home.html') 

    return app

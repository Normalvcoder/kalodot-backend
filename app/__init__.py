from flask import Flask
from config import Config
from google import genai

# 1. Initialize the Flask application
app = Flask(__name__)

# 2. Apply the settings from your config file
app.config.from_object(Config)

# 3. Initialize the Gemini client using the key from config
client = genai.Client(api_key=app.config['GEMINI_API_KEY'])

# IMPORT AT THE BOTTOM: This prevents a "circular import" crash!
from app import routes
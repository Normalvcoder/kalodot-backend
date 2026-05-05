import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # Fetch the key securely from the .env file
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
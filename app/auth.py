import os
from flask import request, jsonify
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_key = request.headers.get('X-Kalodot-Key')
        server_key = os.environ.get('KALODOT_SECRET_KEY')
        
        # If the key is missing or incorrect, block the request
        if not client_key or client_key != server_key:
            return jsonify({"error": "Unauthorized access. Invalid API Key."}), 401
            
        # If the key is correct, let the original function run
        return f(*args, **kwargs)
        
    return decorated_function
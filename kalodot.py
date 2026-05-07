from app import app


@app.route('/')
def home():
    return "Kalodot Backend is LIVE and Running!", 200

if __name__ == '__main__':
    # Threaded=True allows multiple Godot requests to happen at once
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
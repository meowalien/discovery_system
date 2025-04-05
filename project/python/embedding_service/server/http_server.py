import os

from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/version', methods=['GET'])
def version():
    version_info = os.getenv('VERSION', 'unknown')
    return jsonify({'version': version_info})

def serve():
    from waitress import serve
    print(f"HTTP server started on port 8080")
    serve(app, host="0.0.0.0", port=8080)

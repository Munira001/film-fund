from flask import Flask, send_from_directory, request, jsonify
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='frontend/public', static_url_path='')

@app.route('/')
def index():
    return send_from_directory('frontend/public', 'index.html')

@app.route('/<path:path>')
def serve(path):
    try:
        return send_from_directory('frontend/public', path)
    except:
        return send_from_directory('frontend/public', 'index.html')

@app.route('/search-grants', methods=['POST'])
def search_grants():
    try:
        data = request.json
        results = {
            'grants': [],
            'total': 0,
            'message': 'Backend integration ready'
        }
        return jsonify(results), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
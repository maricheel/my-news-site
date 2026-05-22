from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>Diagnostic OK</h1><p>Flask is running. DB will be re-enabled shortly.</p>'

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'flask': 'working'})

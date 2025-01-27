
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/connect', methods=['POST'])
def connect():
    api_key = request.form.get('api_key')
    api_secret = request.form.get('api_secret')
    if api_key and api_secret:
        return jsonify({"status": "success", "message": "API connected"})
    return jsonify({"status": "error", "message": "Missing API credentials"})

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # يسمح لصفحة HTML بالتواصل مع السيرفر بدون مشاكل

@app.route('/')
def home():
    return jsonify({"message": "TikTok Backend Server is Working Live!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

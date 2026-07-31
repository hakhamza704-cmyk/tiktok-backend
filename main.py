from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "TikTok Backend Server is Working Live!"})

@app.route('/download', methods=['POST'])
def download_tiktok():
    data = request.get_json()
    video_url = data.get('url') if data else None

    if not video_url:
        return jsonify({"error": "الرجاء توفير رابط الفيديو!"}), 400

    try:
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            download_link = info.get('url')
            title = info.get('title', 'TikTok Video')

            return jsonify({
                "success": True,
                "title": title,
                "download_url": download_link
            })
    except Exception as e:
        return jsonify({"error": f"فشل جلب الفيديو: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

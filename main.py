from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import re

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "TikTok Backend Server is Working Live!"})

@app.route('/download', methods=['POST'])
def check_and_download():
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
            
            title = info.get('title', '')
            uploader = info.get('uploader', '')
            uploader_id = info.get('uploader_id', '')
            track = info.get('track', '')
            artist = info.get('artist', '')
            description = info.get('description', '')
            download_link = info.get('url', '')

            # خوارزمية كشف إعادة النشر / السرقة
            is_stolen = False
            reasons = []

            # 1. فحص الكلمات المفتاحية في الوصف والعنوان
            credit_keywords = ['ib:', 'cr:', 'credit:', 'repost', 'remix', 'reuploaded', 'حقوق', 'منقول', 'اعادة نشر']
            combined_text = (title + " " + description).lower()
            
            for kw in credit_keywords:
                if kw in combined_text:
                    is_stolen = True
                    reasons.append(f"يحتوي على إشارة لصاحب المحتوى الأصلي ({kw})")
                    break

            # 2. فحص مطابقة صاحب الفيديو مع صاحب الصوت
            if artist and uploader:
                clean_artist = re.sub(r'[^a-zA-Z0-9]', '', artist).lower()
                clean_uploader = re.sub(r'[^a-zA-Z0-9]', '', uploader_id).lower()
                
                if clean_artist and clean_uploader and clean_artist not in clean_uploader and clean_uploader not in clean_artist:
                    is_stolen = True
                    reasons.append(f"الصوت المستخدم ليس ملكاً للحساب (الصوت لـ: {artist})")

            # صياغة النتيجة النهائية
            status_message = "⚠️ هذا الفيديو يعاد نشره أو يحتوي حقوقاً لغير صاحبه!" if is_stolen else "✅ هذا الفيديو يبدو أصلياً ومستقل!"
            
            return jsonify({
                "success": True,
                "title": title,
                "uploader": uploader,
                "is_stolen": is_stolen,
                "status_message": status_message,
                "reasons": reasons,
                "original_audio_author": artist if artist else "غير محدد",
                "download_url": download_link
            })

    except Exception as e:
        return jsonify({"error": f"فشل تحليل الفيديو: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

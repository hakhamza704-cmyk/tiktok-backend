from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import re

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "TikTok Advanced Backend Server is Working Live!"})

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
            artist = info.get('artist', '')
            description = info.get('description', '')
            download_link = info.get('url', '')

            repost_score = 0
            reasons = []

            # المعيار 1: الكلمات المفتاحية
            credit_keywords = ['ib:', 'cr:', 'credit:', 'repost', 'remix', 'reuploaded', 'حقوق', 'منقول', 'اعادة نشر', 'سارق', 'مسروق']
            combined_text = (title + " " + description).lower()
            
            for kw in credit_keywords:
                if kw in combined_text:
                    repost_score += 40
                    reasons.append(f"الوصف يحتوي على إشارة نقل/حقوق ({kw})")
                    break

            # المعيار 2: فحص الصوت
            if artist and uploader:
                clean_artist = re.sub(r'[^a-zA-Z0-9]', '', artist).lower()
                clean_uploader = re.sub(r'[^a-zA-Z0-9]', '', uploader_id).lower()
                is_original_sound_tag = "original" in artist.lower() or "اصلي" in artist.lower() or "صوت" in artist.lower()
                
                if clean_artist and clean_uploader and clean_artist not in clean_uploader and clean_uploader not in clean_artist:
                    if is_original_sound_tag:
                        repost_score += 35
                        reasons.append(f"الصوت المستخدم مأخوذ من صانع آخر ({artist})")
                    else:
                        repost_score += 15
                        reasons.append(f"استخدام موسيقى ترند/خارجية ({artist})")

            # المعيار 3: طول الوصف
            if len(description.strip()) < 5:
                repost_score += 10
                reasons.append("الوصف قصير جداً أو فارغ")

            is_stolen = repost_score >= 45
            status_message = "⚠️ هذا الفيديو يتضمن محتوى مأخوذاً أو معاد نشره!" if is_stolen else "✅ هذا الفيديو يبدو أصلياً ومستقلاً!"

            return jsonify({
                "success": True,
                "title": title,
                "uploader": uploader,
                "is_stolen": is_stolen,
                "repost_score": min(repost_score, 100),
                "status_message": status_message,
                "reasons": reasons,
                "original_audio_author": artist if artist else "ترند عام / غير محدد",
                "download_url": download_link
            })

    except Exception as e:
        return jsonify({"error": f"فشل تحليل الفيديو: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

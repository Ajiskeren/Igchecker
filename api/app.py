from flask import Flask, request, jsonify, render_template
from instagrapi import Client
import os
import json

app = Flask(__name__, template_folder='../templates')

# Inisialisasi Client (Tanpa Login Password)
cl = Client()

def load_session():
    """Fungsi untuk memuat sesi dari Env Variable Vercel"""
    try:
        # Mengambil data session yang kita simpan di pengaturan Vercel
        session_json = os.environ.get('IG_SESSION') 
        if session_json:
            cl.set_settings(json.loads(session_json))
            return True
        else:
            print("❌ Tidak ada IG_SESSION di Environment Variables")
            return False
    except Exception as e:
        print(f"❌ Gagal load session: {e}")
        return False

# Load session saat aplikasi mulai
load_session()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/check', methods=['POST'])
def check_user():
    data = request.json
    target_username = data.get('username')

    if not target_username:
        return jsonify({'error': 'Username kosong'}), 400

    try:
        # Coba ambil info. Jika error (misal session expired), coba relogin (opsional/risky di Vercel)
        info = cl.user_info_by_username(target_username)
        
        result = {
            'status': 'success',
            'username': info.username,
            'full_name': info.full_name,
            'biography': info.biography,
            'followers': info.follower_count,
            'following': info.following_count,
            'posts': info.media_count,
            'is_private': info.is_private,
            'is_verified': info.is_verified,
            'profile_pic': info.profile_pic_url_hd or info.profile_pic_url
        }
        return jsonify(result)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Handler untuk Vercel Serverless
# Tidak perlu app.run() karena Vercel yang menjalankannya

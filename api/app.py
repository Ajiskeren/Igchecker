from flask import Flask, request, jsonify, render_template
from instagrapi import Client
import os
import json

app = Flask(__name__, template_folder='../templates')

cl = Client()

# --- BAGIAN LOAD SESSION (Sama seperti sebelumnya) ---
def load_session():
    try:
        session_json = os.environ.get('IG_SESSION') 
        if session_json:
            cl.set_settings(json.loads(session_json))
            return True
        else:
            # Jika tes lokal tanpa env, abaikan saja dulu
            return False
    except Exception as e:
        print(f"Warning Session: {e}")
        return False

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
        # Login ulang jika perlu (opsional untuk lokal)
        # cl.login(USERNAME, PASSWORD) 
        
        info = cl.user_info_by_username(target_username)
        
        # --- PERBAIKAN DI SINI ---
        # Kita convert URL gambar menjadi string biasa agar tidak error JSON
        pic_url = info.profile_pic_url_hd or info.profile_pic_url
        
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
            'profile_pic': str(pic_url)  # <--- DIBUNGKUS str()
        }
        return jsonify(result)

    except Exception as e:
        print(f"Error Detail: {e}") # Print error di terminal biar kelihatan
        return jsonify({'status': 'error', 'message': str(e)}), 500

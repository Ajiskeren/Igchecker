from flask import Flask, request, jsonify, render_template
from instagrapi import Client
import os
import json
import requests
import base64

app = Flask(__name__, template_folder='../templates')

cl = Client()

# --- LOAD SESSION ---
def load_session():
    try:
        session_json = os.environ.get('IG_SESSION') 
        if session_json:
            cl.set_settings(json.loads(session_json))
            return True
        return False
    except Exception as e:
        print(f"Warning Session: {e}")
        return False

load_session()

def image_to_base64(url):
    """
    Fungsi sakti: Mendownload gambar dari URL Instagram
    dan mengubahnya menjadi kode Base64 agar bisa muncul di semua browser.
    """
    try:
        if not url: return None
        response = requests.get(url)
        if response.status_code == 200:
            # Ubah binary gambar menjadi string base64
            encoded_string = base64.b64encode(response.content).decode('utf-8')
            return f"data:image/jpeg;base64,{encoded_string}"
        return None
    except Exception as e:
        print(f"Gagal convert gambar: {e}")
        return None

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
        # Ambil info user
        info = cl.user_info_by_username(target_username)
        
        # Ambil URL Asli
        raw_url = info.profile_pic_url_hd or info.profile_pic_url
        
        # --- KONVERSI KE BASE64 (SOLUSI PAMUNGKAS) ---
        # Kita download gambarnya di server, bukan di browser user
        base64_image = image_to_base64(raw_url)
        
        # Jika gagal convert, pakai placeholder default
        if not base64_image:
            base64_image = "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png"

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
            'profile_pic': base64_image  # <-- Mengirim data gambar langsung, bukan link
        }
        return jsonify(result)

    except Exception as e:
        print(f"Error Detail: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

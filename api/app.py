from flask import Flask, request, jsonify, render_template
from instagrapi import Client
import os
import json
import requests
import base64
import time
import random

app = Flask(__name__, template_folder='../templates')

cl = Client()

def load_session():
    try:
        session_json = os.environ.get('IG_SESSION') 
        if session_json:
            cl.set_settings(json.loads(session_json))
            return True
        return False
    except: return False

load_session()

def image_to_base64(url):
    """Convert gambar ke Base64 dengan Timeout ketat"""
    try:
        if not url: return None
        # Timeout sangat singkat agar server tidak hang
        response = requests.get(url, timeout=2) 
        if response.status_code == 200:
            encoded_string = base64.b64encode(response.content).decode('utf-8')
            return f"data:image/jpeg;base64,{encoded_string}"
        return "https://via.placeholder.com/150?text=Error+Img"
    except:
        return "https://via.placeholder.com/150?text=Timeout"

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
        # 1. Info Dasar (Biasanya jarang kena limit)
        info = cl.user_info_by_username(target_username)
        user_id = info.pk
        
        # Jeda sedetik biar dikira manusia
        time.sleep(random.uniform(1, 2))

        # Convert PP
        pp_base64 = image_to_base64(info.profile_pic_url_hd or info.profile_pic_url)

        result = {
            'status': 'success',
            'user': {
                'username': info.username,
                'full_name': info.full_name,
                'biography': info.biography,
                'followers_count': info.follower_count,
                'following_count': info.following_count,
                'media_count': info.media_count,
                'is_private': info.is_private,
                'is_verified': info.is_verified,
                'profile_pic': pp_base64
            },
            'posts': [],
            'followers': [],
            'following': [],
            'logs': [] # Untuk memberi info ke user jika ada data yang gagal diambil
        }

        # Jika Private, stop disini
        if info.is_private:
            result['logs'].append("Akun Private: Tidak bisa ambil data lanjutan.")
            return jsonify(result)

        # 2. AMBIL POST (Gunakan Try-Except terpisah)
        try:
            # Ambil cuma 3 post dulu biar ringan & aman
            medias = cl.user_medias(user_id, amount=3)
            for m in medias:
                thumb_base64 = image_to_base64(m.thumbnail_url or m.resources[0].thumbnail_url if m.resources else None)
                result['posts'].append({
                    'caption': m.caption_text[:50] + "..." if m.caption_text else "",
                    'link': f"https://instagram.com/p/{m.code}",
                    'thumbnail': thumb_base64
                })
        except Exception as e:
            result['logs'].append(f"Gagal ambil Post: {str(e)}")

        # 3. AMBIL FOLLOWERS (Try-Except terpisah)
        # Bagian ini yang paling sering kena blokir
        try:
            time.sleep(1) # Jeda lagi
            # Ambil 10 saja cukup untuk demo
            f_data = cl.user_followers(user_id, amount=12)
            for uid, user in f_data.items():
                result['followers'].append({
                    'username': user.username,
                    'full_name': user.full_name,
                    'link': f"https://instagram.com/{user.username}"
                })
        except Exception as e:
            # Jika followers gagal, jangan error 500. Tetap tampilkan profile!
            result['logs'].append("Gagal ambil Followers (Mungkin kena limit IG).")

        # 4. AMBIL FOLLOWING
        try:
            time.sleep(0.5)
            f_ing_data = cl.user_following(user_id, amount=12)
            for uid, user in f_ing_data.items():
                result['following'].append({
                    'username': user.username,
                    'full_name': user.full_name,
                    'link': f"https://instagram.com/{user.username}"
                })
        except Exception as e:
            result['logs'].append("Gagal ambil Following.")

        return jsonify(result)

    except Exception as e:
        # Error fatal (misal login session mati total)
        return jsonify({'status': 'error', 'message': f"Akun Tumbal Bermasalah: {str(e)}"}), 500

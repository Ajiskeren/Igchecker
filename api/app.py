from flask import Flask, request, jsonify, render_template
from instagrapi import Client
import os
import json
import requests
import base64

app = Flask(__name__, template_folder='../templates')

cl = Client()

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
    """Convert gambar ke Base64 (Untuk Profile Pic saja agar cepat)"""
    try:
        if not url: return None
        response = requests.get(url, timeout=5) # Timeout biar gak lama
        if response.status_code == 200:
            encoded_string = base64.b64encode(response.content).decode('utf-8')
            return f"data:image/jpeg;base64,{encoded_string}"
        return None
    except:
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
        # 1. Ambil Info Dasar
        info = cl.user_info_by_username(target_username)
        user_id = info.pk
        
        # Convert Profile Pic (Wajib Base64)
        pp_base64 = image_to_base64(info.profile_pic_url_hd or info.profile_pic_url) or "https://via.placeholder.com/150"

        # Data dasar
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
                'profile_pic': pp_base64,
                'external_url': info.external_url
            },
            'posts': [],
            'followers': [],
            'following': []
        }

        # JIKA AKUN PRIVATE DAN KITA TIDAK FOLLOW, STOP DISINI
        # (Kita tidak bisa melihat post/follower akun private)
        if info.is_private: 
            # Cek apakah akun tumbal kita memfollow dia? (Biasanya tidak)
            # Jadi kita anggap saja tidak bisa ambil data lanjutan
            result['note'] = "Akun Private. Data postingan & network tidak bisa diakses."
            return jsonify(result)

        # 2. Ambil 5 Postingan Terakhir (Media)
        try:
            medias = cl.user_medias(user_id, amount=5)
            for m in medias:
                # Kita tidak base64 gambar post agar tidak timeout (berat), pakai URL saja
                # Frontend akan pakai referrerpolicy="no-referrer"
                thumb = m.thumbnail_url or m.resources[0].thumbnail_url if m.resources else None
                if not thumb and m.product_type == 'feed': thumb = m.thumbnail_url 
                
                result['posts'].append({
                    'caption': m.caption_text[:100] + "..." if m.caption_text else "",
                    'likes': m.like_count,
                    'comments': m.comment_count,
                    'link': f"https://instagram.com/p/{m.code}",
                    'thumbnail': str(thumb or "")
                })
        except Exception as e:
            print(f"Gagal ambil post: {e}")

        # 3. Ambil Sample Followers (Maks 10 biar cepat)
        try:
            # cl.user_followers mengembalikan dict {id: User}
            followers_data = cl.user_followers(user_id, amount=10)
            for uid, user in followers_data.items():
                result['followers'].append({
                    'username': user.username,
                    'full_name': user.full_name,
                    'link': f"https://instagram.com/{user.username}"
                })
        except Exception as e:
            print(f"Gagal ambil followers: {e}")

        # 4. Ambil Sample Following (Maks 10 biar cepat)
        try:
            following_data = cl.user_following(user_id, amount=10)
            for uid, user in following_data.items():
                result['following'].append({
                    'username': user.username,
                    'full_name': user.full_name,
                    'link': f"https://instagram.com/{user.username}"
                })
        except Exception as e:
            print(f"Gagal ambil following: {e}")

        return jsonify(result)

    except Exception as e:
        print(f"Error Utama: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

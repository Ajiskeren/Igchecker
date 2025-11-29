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
    """Download gambar dan ubah jadi kode Base64 agar anti-blokir"""
    try:
        if not url: return None
        # Timeout singkat (3 detik) agar proses keseluruhan tidak lama
        response = requests.get(url, timeout=3) 
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
        # 1. Info Dasar
        info = cl.user_info_by_username(target_username)
        user_id = info.pk
        
        # Profile Pic Base64
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
                'profile_pic': pp_base64 or "https://via.placeholder.com/150"
            },
            'posts': [],
            'followers': [],
            'following': []
        }

        if info.is_private:
            result['note'] = "Akun Private"
            return jsonify(result)

        # 2. Ambil 6 Postingan Terakhir (Kita convert gambarnya ke Base64)
        try:
            medias = cl.user_medias(user_id, amount=6)
            for m in medias:
                # Logika mencari URL thumbnail yang valid
                thumb_url = m.thumbnail_url
                if not thumb_url and m.resources:
                    thumb_url = m.resources[0].thumbnail_url
                
                # Convert ke Base64 (PENTING AGAR MUNCUL)
                thumb_base64 = image_to_base64(thumb_url)

                result['posts'].append({
                    'caption': m.caption_text[:80] + "..." if m.caption_text else "",
                    'likes': m.like_count,
                    'comments': m.comment_count,
                    'link': f"https://instagram.com/p/{m.code}",
                    'thumbnail': thumb_base64 or "https://via.placeholder.com/300?text=No+Image"
                })
        except Exception as e:
            print(f"Err Post: {e}")

        # 3. Ambil 50 Followers (Disimpan di memori browser nanti)
        try:
            f_data = cl.user_followers(user_id, amount=50)
            for uid, user in f_data.items():
                result['followers'].append({
                    'username': user.username,
                    'full_name': user.full_name,
                    'link': f"https://instagram.com/{user.username}"
                })
        except: pass

        # 4. Ambil 50 Following
        try:
            f_ing_data = cl.user_following(user_id, amount=50)
            for uid, user in f_ing_data.items():
                result['following'].append({
                    'username': user.username,
                    'full_name': user.full_name,
                    'link': f"https://instagram.com/{user.username}"
                })
        except: pass

        return jsonify(result)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

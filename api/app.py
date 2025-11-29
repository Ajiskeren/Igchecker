<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Checker API</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #fafafa; text-align: center; padding: 20px; color: #262626; }
        .container { max-width: 400px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); border: 1px solid #dbdbdb; }
        h2 { margin-bottom: 20px; color: #262626; }
        
        input { 
            width: 80%; padding: 12px; margin: 10px 0; 
            border: 1px solid #dbdbdb; border-radius: 6px; 
            background: #fafafa; outline: none;
        }
        input:focus { border: 1px solid #a8a8a8; }
        
        button { 
            padding: 10px 24px; background: #0095f6; color: white; 
            border: none; border-radius: 6px; cursor: pointer; font-weight: 600; 
            transition: background 0.2s;
        }
        button:hover { background: #0077c2; }
        button:disabled { background: #b2dffc; cursor: not-allowed; }

        #result { margin-top: 30px; text-align: left; display: none; border-top: 1px solid #efefef; padding-top: 20px; }
        .profile-header { text-align: center; margin-bottom: 20px; }
        
        /* PENTING: Class untuk gambar profil */
        .profile-img { 
            width: 120px; height: 120px; 
            border-radius: 50%; object-fit: cover; 
            border: 4px solid #fff; 
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            margin-bottom: 10px;
        }
        
        .verified { color: #0095f6; margin-left: 4px; }
        
        .stats { display: flex; justify-content: space-around; margin: 20px 0; border-bottom: 1px solid #efefef; padding-bottom: 20px; }
        .stat-box { text-align: center; }
        .stat-val { font-weight: bold; font-size: 18px; display: block; }
        .stat-label { font-size: 12px; color: #8e8e8e; }
        
        .bio { 
            white-space: pre-wrap; font-size: 14px; color: #262626; line-height: 1.5;
            background: #fafafa; padding: 10px; border-radius: 8px; margin-top: 10px;
        }
        
        .error-msg { color: red; margin-top: 10px; font-size: 14px; }
    </style>
</head>
<body>

<div class="container">
    <h2>🔍 IG Profile Checker</h2>
    <input type="text" id="usernameInput" placeholder="Username (tanpa @)" autocomplete="off">
    <br>
    <button onclick="checkInstagram()" id="btnCheck">Cek Akun</button>

    <div id="loading" style="display:none; margin-top:20px; color:#8e8e8e;">
        ⏳ Sedang mengambil data dari Instagram...
    </div>
    
    <div id="error" class="error-msg" style="display:none;"></div>

    <div id="result">
        <div class="profile-header">
            <!-- PENTING: referrerpolicy="no-referrer" agar gambar muncul -->
            <img id="pp" src="" class="profile-img" alt="Profile Pic" referrerpolicy="no-referrer">
            
            <h3 id="fullname" style="margin: 5px 0;">Nama Lengkap</h3>
            <p id="username" style="color:#8e8e8e; margin:0;">@username</p>
            <small id="is_private" style="color: #ed4956; font-weight:bold; display:none;">🔒 Private Account</small>
        </div>

        <div class="stats">
            <div class="stat-box"><span class="stat-val" id="posts">0</span><span class="stat-label">Posts</span></div>
            <div class="stat-box"><span class="stat-val" id="followers">0</span><span class="stat-label">Followers</span></div>
            <div class="stat-box"><span class="stat-val" id="following">0</span><span class="stat-label">Following</span></div>
        </div>

        <p style="font-weight:600; margin-bottom:5px;">Biografi:</p>
        <div class="bio" id="bio">-</div>
    </div>
</div>

<script>
    async function checkInstagram() {
        const usernameInput = document.getElementById('usernameInput');
        const username = usernameInput.value.trim();
        const resultDiv = document.getElementById('result');
        const loadingDiv = document.getElementById('loading');
        const errorDiv = document.getElementById('error');
        const btn = document.getElementById('btnCheck');
        
        if (!username) return;

        // Reset tampilan
        resultDiv.style.display = 'none';
        errorDiv.style.display = 'none';
        loadingDiv.style.display = 'block';
        btn.disabled = true;

        try {
            const response = await fetch('/api/check', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: username })
            });

            const data = await response.json();
            loadingDiv.style.display = 'none';
            btn.disabled = false;

            if (data.status === 'success') {
                // Set Gambar
                const imgElement = document.getElementById('pp');
                imgElement.src = data.profile_pic;
                
                // Set Data Teks
                let nameHtml = data.full_name;
                if(data.is_verified) nameHtml += ' <span class="verified">☑️</span>';
                
                document.getElementById('fullname').innerHTML = nameHtml || data.username;
                document.getElementById('username').innerText = "@" + data.username;
                document.getElementById('posts').innerText = data.posts.toLocaleString();
                document.getElementById('followers').innerText = data.followers.toLocaleString();
                document.getElementById('following').innerText = data.following.toLocaleString();
                document.getElementById('bio').innerText = data.biography || "(Tidak ada bio)";
                
                // Cek Private
                const privateLabel = document.getElementById('is_private');
                privateLabel.style.display = data.is_private ? 'block' : 'none';
                
                resultDiv.style.display = 'block';
            } else {
                errorDiv.innerText = "Gagal: " + (data.message || "Akun tidak ditemukan/Error server");
                errorDiv.style.display = 'block';
            }
        } catch (error) {
            loadingDiv.style.display = 'none';
            btn.disabled = false;
            errorDiv.innerText = "Terjadi kesalahan koneksi ke server.";
            errorDiv.style.display = 'block';
            console.error(error);
        }
    }
    
    // Enter key support
    document.getElementById("usernameInput").addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            event.preventDefault();
            document.getElementById("btnCheck").click();
        }
    });
</script>

</body>
</html>


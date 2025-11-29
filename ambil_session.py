# Jalankan ini SEKALI saja di laptop untuk dapat session string
from instagrapi import Client
import json

USERNAME = 'yaudahsih_gapapa'
PASSWORD = 'KAMUBERTANYa123123'

cl = Client()
cl.login(USERNAME, PASSWORD)

# Simpan session ke format text
session_data = cl.get_settings()
print("\n=== COPY KODE DI BAWAH INI KE VERCEL ENVIRONMENT VARIABLE ===")
print(json.dumps(session_data))
print("=============================================================")

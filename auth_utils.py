import bcrypt
import os
from supabase import create_client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def registrar_usuario_seguro(username, password):
    hash_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    data = {
        "username": username,
        "password_hash": hash_password.decode('utf-8'),
        "rol": "admin"
    }
    return supabase.table("usuarios").insert(data).execute()

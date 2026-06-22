import bcrypt
import os
from supabase import create_client

# Conexión a la base de datos (usando las credenciales de tu .env)
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def verificar_login(username, password_input):
    # Buscamos al usuario
    usuario = supabase.table("usuarios").select("password_hash").eq("username", username).execute().data
    
    if usuario:
        hash_en_db = usuario[0]['password_hash'].encode('utf-8')
        # Comparamos la contraseña ingresada con la guardada
        if bcrypt.checkpw(password_input.encode('utf-8'), hash_en_db):
            return True
    return False

def crear_usuario(username, password):
    # Ciframos la contraseña antes de guardarla
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hash_password = bcrypt.hashpw(password_bytes, salt)
    
    return supabase.table("usuarios").insert({
        "username": username,
        "password_hash": hash_password.decode('utf-8')
    }).execute()
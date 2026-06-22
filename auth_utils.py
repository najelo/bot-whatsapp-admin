import os
import bcrypt
from supabase import create_client

def get_supabase():
    # Obtenemos las credenciales desde los Secrets de Streamlit
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    return create_client(url, key)

def verificar_login(username, password_input):
    supabase = get_supabase()
    # Buscamos al usuario
    response = supabase.table("usuarios").select("*").eq("username", username).execute()
    
    if not response.data:
        return False, "Usuario no encontrado"

    user_data = response.data[0]
    hash_guardado = user_data["password_hash"].encode('utf-8')
    
    # Verificamos la contraseña
    if bcrypt.checkpw(password_input.encode('utf-8'), hash_guardado):
        return True, "Login exitoso"
    return False, "Contraseña incorrecta"

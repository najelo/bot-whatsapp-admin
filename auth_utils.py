import os
import bcrypt
from supabase import create_client

def get_supabase():
    # Obtenemos las variables de entorno dentro de la función para mayor seguridad
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        return None # Retornamos None si no hay credenciales
    return create_client(url, key)

def verificar_login(username, password_input):
    supabase = get_supabase()
    if not supabase:
        return False, "Error de configuración: No hay conexión a la base de datos."
        
    response = supabase.table("usuarios").select("*").eq("username", username).execute()
    
    if not response.data:
        return False, "Usuario no encontrado"

    user_data = response.data[0]
    hash_guardado = user_data["password_hash"].encode('utf-8')
    
    if bcrypt.checkpw(password_input.encode('utf-8'), hash_guardado):
        return True, "Login exitoso"
    else:
        return False, "Contraseña incorrecta"

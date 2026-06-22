import os
import bcrypt
from dotenv import load_dotenv
from supabase import create_client

# Cargar variables
load_dotenv(override=True)

# Crear el cliente dentro de una función o como variable global accesible
def get_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    return create_client(url, key)

def verificar_login(username, password_input):
    supabase = get_supabase() # <-- Obtenemos el cliente aquí dentro
    
    # 1. Buscar el usuario
    usuario = supabase.table("usuarios").select("*").eq("username", username).execute()
    
    if not usuario.data:
        return False, "Usuario no encontrado"

    hash_guardado = usuario.data[0]["password_hash"].encode('utf-8')
    
    # 2. Comparar contraseñas
    if bcrypt.checkpw(password_input.encode('utf-8'), hash_guardado):
        return True, "Login exitoso"
    else:
        return False, "Contraseña incorrecta"

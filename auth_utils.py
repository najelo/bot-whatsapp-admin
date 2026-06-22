import os
import bcrypt
from supabase import create_client

# 1. Intentar cargar variables locales si existen (solo para desarrollo en tu PC)
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass  # Si no está instalado o no se necesita, no importa

# 2. Obtener las credenciales
def get_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    return create_client(url, key)
if not url or not key:
    raise Exception("ERROR: Las variables SUPABASE_URL o SUPABASE_KEY no están configuradas.")

# 4. Crear cliente de Supabase
supabase = create_client(url, key)

def verificar_login(username, password_input):
    """
    Verifica si el usuario y contraseña son correctos.
    """
    # Buscar el usuario en la tabla
    response = supabase.table("usuarios").select("*").eq("username", username).execute()
    
    if not response.data:
        return False, "Usuario no encontrado"

    user_data = response.data[0]
    hash_guardado = user_data["password_hash"].encode('utf-8')
    
    # Verificar contraseña cifrada
    if bcrypt.checkpw(password_input.encode('utf-8'), hash_guardado):
        return True, "Login exitoso"
    else:
        return False, "Contraseña incorrecta"

def registrar_usuario_seguro(username, password):
    """
    Registra un nuevo usuario con contraseña cifrada (úselo solo para el admin).
    """
    hash_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    data = {
        "username": username,
        "password_hash": hash_password.decode('utf-8'),
        "rol": "admin"
    }
    return supabase.table("usuarios").insert(data).execute()

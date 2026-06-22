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
    try:
        # Intentamos obtener solo la fila donde el usuario coincide
        response = supabase.table("usuarios").select("password_hash").eq("username", username).execute()
        
        if not response.data:
            return False, "Usuario no encontrado"
        
        # Obtenemos el hash de la lista
        hash_guardado = response.data[0]["password_hash"].encode('utf-8')
        
        if bcrypt.checkpw(password_input.encode('utf-8'), hash_guardado):
            return True, "Login exitoso"
        else:
            return False, "Contraseña incorrecta"
            
    except Exception as e:
        # Esto imprimirá el error real en los logs de Streamlit
        print(f"--- ERROR DE SUPABASE ---")
        print(e)
        return False, "Error interno de base de datos"
        return True, "Login exitoso"
    return False, "Contraseña incorrecta"

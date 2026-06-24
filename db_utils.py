import uuid
from auth_utils import get_supabase

def obtener_configuraciones():
    try:
        response = get_supabase().table("clientes").select("*, respuestas(*)").execute()
        return response.data
    except Exception as e:
        print(f"Error al obtener configuraciones: {e}")
        return []

def subir_archivo_al_storage(archivo_bytes, nombre_archivo, bucket_name):
    """Sube archivos (img/audio/pdf) a Supabase y devuelve la URL."""
    try:
        supabase = get_supabase()
        nombre_unico = f"{uuid.uuid4()}_{nombre_archivo}"
        supabase.storage.from_(bucket_name).upload(path=nombre_unico, file=archivo_bytes)
        return supabase.storage.from_(bucket_name).get_public_url(nombre_unico)
    except Exception as e:
        print(f"Error al subir: {e}")
        return None

def guardar_configuracion(palabra_clave, contenido):
    try:
        supabase = get_supabase()
        res_resp = supabase.table("respuestas").insert({"contenido": contenido}).execute()
        nueva_respuesta_id = res_resp.data[0]['id']
        supabase.table("clientes").insert({
            "palabra_clave": palabra_clave.lower(),
            "respuesta_id": nueva_respuesta_id
        }).execute()
        return True
    except Exception as e:
        print(f"Error al guardar configuración: {e}")
        return False

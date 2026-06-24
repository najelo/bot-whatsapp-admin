import uuid
from auth_utils import get_supabase

def obtener_configuraciones():
    try:
        supabase = get_supabase()
        # Intentamos el JOIN
        response = supabase.table("clientes").select("id, palabra_clave, respuesta_id, respuestas(id, contenido)").execute()
        
        if not response.data:
            return []
        return response.data
    except Exception as e:
        print(f"Error en obtener_configuraciones: {e}")
        return []

def subir_archivo_al_storage(archivo_bytes, nombre_archivo, bucket_name="media-bot"):
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
        # 1. Crear respuesta
        res_resp = supabase.table("respuestas").insert({"contenido": contenido}).execute()
        if not res_resp.data: return False
        
        nueva_respuesta_id = res_resp.data[0]['id']
        # 2. Crear cliente
        supabase.table("clientes").insert({
            "palabra_clave": palabra_clave.lower().strip(),
            "respuesta_id": nueva_respuesta_id
        }).execute()
        return True
    except Exception as e:
        print(f"Error al guardar: {e}")
        return False

import uuid
from auth_utils import get_supabase

def obtener_configuraciones():
    try:
        return get_supabase().table("clientes").select("id, palabra_clave, respuesta_id, respuestas(id, contenido)").execute().data
    except Exception as e:
        print(f"Error al obtener configuraciones: {e}")
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

def listar_archivos_storage(bucket_name="media-bot"):
    try:
        files = get_supabase().storage.from_(bucket_name).list()
        return [f["name"] for f in files]
    except Exception:
        return []

def guardar_configuracion(palabras_clave, respuesta_texto):
    try:
        supabase = get_supabase()
        res_resp = supabase.table("respuestas").insert({"contenido": respuesta_texto}).execute()
        nuevo_id = res_resp.data[0]['id']
        lista = [p.strip() for p in palabras_clave.split(',')]
        for palabra in lista:
            if palabra:
                supabase.table("clientes").insert({"palabra_clave": palabra.lower(), "respuesta_id": nuevo_id}).execute()
        return True
    except Exception as e:
        print(f"Error al guardar: {e}")
        return False

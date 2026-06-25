import uuid
from auth_utils import get_supabase

def obtener_configuraciones():
    """Trae todas las reglas configuradas."""
    try:
        # Traemos la palabra, la respuesta y el tipo de contenido
        return get_supabase().table("clientes").select("id, palabra_clave, respuesta_id, respuestas(id, contenido, tipo_contenido)").execute().data
    except Exception as e:
        print(f"Error al obtener: {e}")
        return []

def subir_archivo_al_storage(archivo_bytes, nombre_archivo, bucket_name="recetarios-helado"):
    """Sube un archivo a Supabase Storage y devuelve la URL pública."""
    try:
        supabase = get_supabase()
        nombre_unico = f"{uuid.uuid4()}_{nombre_archivo}"
        supabase.storage.from_(bucket_name).upload(path=nombre_unico, file=archivo_bytes)
        return supabase.storage.from_(bucket_name).get_public_url(nombre_unico)
    except Exception as e:
        print(f"Error al subir: {e}")
        return None

def guardar_configuracion(palabras, contenido, tipo="text"):
    """
    Guarda la respuesta en la tabla 'respuestas' y asocia las palabras clave.
    'tipo' debe ser 'text' o 'document'.
    """
    try:
        supabase = get_supabase()
        
        # 1. Insertamos el contenido y su tipo en la tabla respuestas
        res = supabase.table("respuestas").insert({
            "contenido": contenido,
            "tipo_contenido": tipo
        }).execute()
        
        rid = res.data[0]['id']
        
        # 2. Asociamos cada palabra clave con el ID de esta respuesta
        for p in [p.strip() for p in palabras.split(',')]:
            if p: 
                supabase.table("clientes").insert({
                    "palabra_clave": p.lower(),
                    "respuesta_id": rid
                }).execute()
        return True
    except Exception as e:
        print(f"Error al guardar configuración: {e}")
        return False

def eliminar_regla(cliente_id, respuesta_id):
    """Elimina una palabra clave y, si no hay más palabras usando esa respuesta, elimina la respuesta."""
    try:
        supabase = get_supabase()
        # 1. Eliminamos la relación en clientes
        supabase.table("clientes").delete().eq("id", cliente_id).execute()
        
        # 2. Verificamos si alguien más usa esta respuesta
        otras = supabase.table("clientes").select("id").eq("respuesta_id", respuesta_id).execute()
        if not otras.data:
            supabase.table("respuestas").delete().eq("id", respuesta_id).execute()
        
        return True
    except Exception as e:
        print(f"Error al eliminar: {e}")
        return False

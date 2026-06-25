import uuid
from auth_utils import get_supabase

def obtener_configuraciones():
    try:
        return get_supabase().table("clientes").select(
            "id, palabra_clave, respuesta_id, respuestas(id, contenido, tipo_contenido)"
        ).execute().data
    except Exception as e:
        print(f"Error al obtener: {e}")
        return []

def subir_archivo_al_storage(archivo_bytes, nombre_archivo, bucket_name="recetarios-helado"):
    try:
        supabase = get_supabase()
        nombre_unico = f"{uuid.uuid4()}_{nombre_archivo}"
        supabase.storage.from_(bucket_name).upload(path=nombre_unico, file=archivo_bytes)
        return supabase.storage.from_(bucket_name).get_public_url(nombre_unico)
    except Exception as e:
        print(f"Error al subir: {e}")
        return None

def listar_archivos_storage(bucket_name="recetarios-helado"):
    try:
        lista = get_supabase().storage.from_(bucket_name).list()
        return [f["name"] for f in lista if f["name"].endswith(".pdf")]
    except Exception: return []

def guardar_configuracion(palabras, contenido, tipo_contenido="texto"):
    """
    Guarda la respuesta incluyendo obligatoriamente el tipo_contenido 
    para cumplir con la estructura de Supabase.
    """
    try:
        supabase = get_supabase()
        
        # 1. Insertamos incluyendo el tipo_contenido requerido por tu base de datos
        res = supabase.table("respuestas").insert({
            "contenido": contenido,
            "tipo_contenido": tipo_contenido
        }).execute()
        
        if not res.data:
            return False
            
        rid = res.data[0]['id']
        
        # 2. Enlazamos las palabras clave
        for p in [p.strip().lower() for p in palabras.split(',')]:
            if p: 
                supabase.table("clientes").insert({
                    "palabra_clave": p, 
                    "respuesta_id": rid
                }).execute()
        return True
    except Exception as e:
        print(f"Error en inserción: {e}")
        return False

def eliminar_regla(cliente_id, respuesta_id):
    try:
        supabase = get_supabase()
        supabase.table("clientes").delete().eq("id", cliente_id).execute()
        supabase.table("respuestas").delete().eq("id", respuesta_id).execute()
        return True
    except: return False

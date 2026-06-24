import uuid
from auth_utils import get_supabase

def obtener_configuraciones():
    try:
        return get_supabase().table("clientes").select("id, palabra_clave, respuesta_id, respuestas(id, contenido)").execute().data
    except Exception as e:
        print(f"Error al obtener configuraciones: {e}")
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
    """Lista los archivos PDF directamente desde tu bucket de Supabase."""
    try:
        supabase = get_supabase()
        lista = supabase.storage.from_(bucket_name).list()
        return [f["name"] for f in lista if f["name"].endswith(".pdf")]
    except Exception as e:
        print(f"Error listando archivos: {e}")
        return []

def guardar_configuracion(palabras, contenido):
    try:
        supabase = get_supabase()
        res = supabase.table("respuestas").insert({"contenido": contenido}).execute()
        rid = res.data[0]['id']
        for p in [p.strip() for p in palabras.split(',')]:
            if p:
                supabase.table("clientes").insert({"palabra_clave": p.lower(), "respuesta_id": rid}).execute()
        return True
    except Exception as e:
        print(f"Error al guardar: {e}")
        return False

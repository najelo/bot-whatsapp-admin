from auth_utils import get_supabase

def obtener_configuraciones():
    try:
        supabase = get_supabase()
        response = supabase.table("config_bot").select("*").execute()
        return response.data
    except Exception:
        return []

def guardar_configuracion(clave, respuesta):
    try:
        supabase = get_supabase()
        supabase.table("config_bot").insert({
            "clave_busqueda": clave,
            "respuesta_bot": respuesta
        }).execute()
        return True, "Guardado exitosamente"
    except Exception as e:
        return False, str(e)

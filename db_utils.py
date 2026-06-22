from auth_utils import get_supabase

def obtener_palabras_clave():
    """Trae todas las configuraciones del bot."""
    supabase = get_supabase()
    try:
        response = supabase.table("config_bot").select("*").execute()
        return response.data
    except Exception:
        return []

def guardar_configuracion(clave, respuesta, telefono):
    """Guarda una nueva palabra clave y respuesta."""
    supabase = get_supabase()
    try:
        supabase.table("config_bot").insert({
            "clave_busqueda": clave,
            "respuesta_bot": respuesta,
            "numero_telefono": telefono
        }).execute()
        return True, "Configuración guardada exitosamente"
    except Exception as e:
        return False, str(e)

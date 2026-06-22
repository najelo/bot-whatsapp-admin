from auth_utils import get_supabase

def obtener_configuracion_bot():
    supabase = get_supabase()
    try:
        return supabase.table("config_bot").select("*").execute().data
    except Exception as e:
        return None # O maneja el error aquí mismo

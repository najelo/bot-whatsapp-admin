from auth_utils import get_supabase

def obtener_configuraciones():
    """Trae las palabras clave y sus respuestas relacionadas."""
    try:
        supabase = get_supabase()
        response = supabase.table("clientes").select("id, palabra_clave, respuesta_id, respuestas(contenido)").execute()
        return response.data
    except Exception:
        return []

def guardar_configuracion(palabra, respuesta_texto):
    """Guarda primero la respuesta y luego la relaciona con la palabra clave."""
    try:
        supabase = get_supabase()
        res_resp = supabase.table("respuestas").insert({"contenido": respuesta_texto}).execute()
        nuevo_id = res_resp.data[0]['id']
        supabase.table("clientes").insert({"palabra_clave": palabra, "respuesta_id": nuevo_id}).execute()
        return True, "Configuración guardada correctamente"
    except Exception as e:
        return False, f"Error al guardar: {str(e)}"

# --- NUEVO CÓDIGO ---

def eliminar_configuracion(id_config):
    try:
        get_supabase().table("clientes").delete().eq("id", id_config).execute()
        return True, "Eliminado"
    except Exception as e:
        return False, str(e)

def actualizar_configuracion(id_config, nueva_palabra, nuevo_id_respuesta):
    try:
        get_supabase().table("clientes").update({
            "palabra_clave": nueva_palabra,
            "respuesta_id": nuevo_id_respuesta
        }).eq("id", id_config).execute()
        return True, "Actualizado"
    except Exception as e:
        return False, str(e)

def obtener_todas_las_respuestas():
    try:
        return get_supabase().table("respuestas").select("*").execute().data
    except Exception:
        return []

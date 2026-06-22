from auth_utils import get_supabase

def obtener_configuraciones():
    try:
        supabase = get_supabase()
        response = supabase.table("clientes").select("id, palabra_clave, respuesta_id, respuestas(contenido)").execute()
        return response.data
    except Exception:
        return []

def guardar_configuracion(palabra, respuesta_texto):
    try:
        supabase = get_supabase()
        res_resp = supabase.table("respuestas").insert({"contenido": respuesta_texto}).execute()
        nuevo_id = res_resp.data[0]['id']
        supabase.table("clientes").insert({"palabra_clave": palabra, "respuesta_id": nuevo_id}).execute()
        return True, "Configuración guardada"
    except Exception as e:
        return False, str(e)

# Asegúrate de que estas funciones estén tal cual aquí:
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

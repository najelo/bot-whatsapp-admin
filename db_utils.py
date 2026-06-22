from auth_utils import get_supabase

def obtener_configuraciones():
    try:
        supabase = get_supabase()
        return supabase.table("clientes").select("id, palabra_clave, respuesta_id, respuestas(contenido)").execute().data
    except Exception:
        return []

def guardar_configuracion(palabras_clave, respuesta_texto):
    """Guarda múltiples palabras clave vinculadas a una misma respuesta."""
    try:
        supabase = get_supabase()
        # 1. Crear la respuesta única
        res_resp = supabase.table("respuestas").insert({"contenido": respuesta_texto}).execute()
        nuevo_id = res_resp.data[0]['id']
        
        # 2. Guardar cada palabra clave por separado
        lista = [p.strip() for p in palabras_clave.split(',')]
        for palabra in lista:
            supabase.table("clientes").insert({
                "palabra_clave": palabra.lower(),
                "respuesta_id": nuevo_id
            }).execute()
        return True, "Reglas guardadas con éxito"
    except Exception as e:
        return False, str(e)

def eliminar_configuracion(id_config):
    try:
        get_supabase().table("clientes").delete().eq("id", id_config).execute()
        return True, "Eliminado"
    except Exception as e:
        return False, str(e)

def actualizar_configuracion(id_config, nueva_palabra, nuevo_id_respuesta):
    try:
        get_supabase().table("clientes").update({
            "palabra_clave": nueva_palabra.lower().strip(),
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

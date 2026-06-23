from auth_utils import get_supabase

def obtener_configuraciones():
    """Trae las palabras clave y sus respuestas relacionadas."""
    try:
        supabase = get_supabase()
        # Consulta las tablas relacionadas
        response = supabase.table("clientes").select("id, palabra_clave, respuesta_id, respuestas(contenido)").execute()
        return response.data
    except Exception:
        return []

def obtener_todas_las_respuestas():
    """Trae todas las respuestas disponibles para el selector."""
    try:
        return get_supabase().table("respuestas").select("*").execute().data
    except Exception:
        return []

def guardar_configuracion(palabras_clave, respuesta_texto):
    """Guarda una respuesta nueva y vincula múltiples palabras clave."""
    try:
        supabase = get_supabase()
        res_resp = supabase.table("respuestas").insert({"contenido": respuesta_texto}).execute()
        nuevo_id = res_resp.data[0]['id']
        
        lista = [p.strip() for p in palabras_clave.split(',')]
        for palabra in lista:
            if palabra:
                supabase.table("clientes").insert({
                    "palabra_clave": palabra.lower(),
                    "respuesta_id": nuevo_id
                }).execute()
        return True, "Reglas guardadas"
    except Exception as e:
        return False, str(e)

def guardar_palabra_individual(palabra, respuesta_id):
    """Guarda una palabra clave vinculada a un ID de respuesta existente."""
    try:
        get_supabase().table("clientes").insert({
            "palabra_clave": palabra.lower().strip(),
            "respuesta_id": respuesta_id
        }).execute()
        return True, "Palabra agregada"
    except Exception as e:
        return False, str(e)

def actualizar_respuesta(respuesta_id, nuevo_contenido):
    """Actualiza el texto de una respuesta existente en la tabla respuestas."""
    try:
        get_supabase().table("respuestas").update({"contenido": nuevo_contenido}).eq("id", respuesta_id).execute()
        return True, "Respuesta actualizada"
    except Exception as e:
        return False, str(e)

def eliminar_configuracion(id_config):
    """Elimina una fila específica de la tabla clientes."""
    try:
        get_supabase().table("clientes").delete().eq("id", id_config).execute()
        return True, "Eliminado"
    except Exception as e:
        return False, str(e)

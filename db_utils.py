from auth_utils import get_supabase

def obtener_configuraciones():
    try:
        supabase = get_supabase()
        response = supabase.table("clientes").select("id, palabra_clave, respuesta_id, respuestas(contenido)").execute()
        return response.data
    except Exception:
        return []

def obtener_todas_las_respuestas():
    try:
        return get_supabase().table("respuestas").select("*").execute().data
    except Exception:
        return []

def guardar_configuracion(palabras_clave, respuesta_texto):
    try:
        supabase = get_supabase()
        res_resp = supabase.table("respuestas").insert({"contenido": respuesta_texto}).execute()
        nuevo_id = res_resp.data[0]['id']
        lista = [p.strip() for p in palabras_clave.split(',')]
        for palabra in lista:
            if palabra:
                supabase.table("clientes").insert({"palabra_clave": palabra.lower(), "respuesta_id": nuevo_id}).execute()
        return True, "Reglas guardadas"
    except Exception as e:
        return False, str(e)

def guardar_respuesta_pdf(contenido_pdf):
    try:
        supabase = get_supabase()
        res = supabase.table("respuestas").insert({"contenido": contenido_pdf}).execute()
        return True, res.data[0]['id']
    except Exception as e:
        return False, str(e)

def guardar_palabra_individual(palabra, respuesta_id):
    try:
        get_supabase().table("clientes").insert({"palabra_clave": palabra.lower().strip(), "respuesta_id": respuesta_id}).execute()
    except Exception:
        pass

def eliminar_configuracion(id_config):
    try:
        get_supabase().table("clientes").delete().eq("id", id_config).execute()
        return True, "Eliminado"
    except Exception as e:
        return False, str(e)

from auth_utils import get_supabase

def obtener_configuraciones():
    try:
        response = get_supabase().table("clientes").select("id, palabra_clave, respuesta_id, respuestas(contenido)").execute()
        return response.data
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
                supabase.table("clientes").insert({
                    "palabra_clave": palabra.lower(),
                    "respuesta_id": nuevo_id
                }).execute()
        return True, "Reglas guardadas"
    except Exception as e:
        return False, str(e)

def actualizar_respuesta(respuesta_id, nuevo_contenido):
    try:
        get_supabase().table("respuestas").update({"contenido": nuevo_contenido}).eq("id", respuesta_id).execute()
        return True, "Actualizado"
    except Exception as e:
        return False, str(e)

def eliminar_configuracion(id_config):
    try:
        get_supabase().table("clientes").delete().eq("id", id_config).execute()
        return True, "Eliminado"
    except Exception as e:
        return False, str(e)

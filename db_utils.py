from auth_utils import get_supabase

def obtener_configuraciones():
    """Trae las palabras clave y sus respuestas relacionadas."""
    try:
        supabase = get_supabase()
        # Consulta las tablas relacionadas
        response = supabase.table("clientes").select("palabra_clave, respuestas(contenido)").execute()
        return response.data
    except Exception:
        return []

def guardar_configuracion(palabra, respuesta_texto):
    """Guarda primero la respuesta y luego la relaciona con la palabra clave."""
    try:
        supabase = get_supabase()
        
        # 1. Insertamos en 'respuestas' para obtener un ID
        res_resp = supabase.table("respuestas").insert({"contenido": respuesta_texto}).execute()
        nuevo_id = res_resp.data[0]['id']
        
        # 2. Insertamos en 'clientes' vinculando el ID obtenido
        supabase.table("clientes").insert({
            "palabra_clave": palabra,
            "respuesta_id": nuevo_id
        }).execute()
        
        return True, "Configuración guardada correctamente"
    except Exception as e:
        return False, f"Error al guardar: {str(e)}"

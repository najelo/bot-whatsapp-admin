from auth_utils import get_supabase

def guardar_configuracion(palabra, contenido):
    """Guarda la palabra clave y su respuesta en Supabase."""
    supabase = get_supabase()
    
    # 1. Insertar el contenido en la tabla 'respuestas'
    res_resp = supabase.table("respuestas").insert({"contenido": contenido}).execute()
    
    # Obtenemos el ID generado por la inserción
    nuevo_id = res_resp.data[0]['id']
    
    # 2. Insertar la regla en la tabla 'clientes' vinculándola al nuevo ID
    supabase.table("clientes").insert({
        "palabra_clave": palabra, 
        "respuesta_id": nuevo_id
    }).execute()

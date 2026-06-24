from auth_utils import get_supabase

def obtener_configuraciones():
    try:
        # Consulta JOIN básica para obtener clientes y sus respuestas
        return get_supabase().table("clientes").select("id, palabra_clave, respuesta_id, respuestas(id, contenido)").execute().data
    except Exception as e:
        print(f"Error al obtener configuraciones: {e}")
        return []

def guardar_configuracion(palabras, contenido):
    try:
        supabase = get_supabase()
        # 1. Guardar la respuesta
        res = supabase.table("respuestas").insert({"contenido": contenido}).execute()
        rid = res.data[0]['id']
        # 2. Vincular a cliente(s)
        for p in [p.strip() for p in palabras.split(',')]:
            if p:
                supabase.table("clientes").insert({"palabra_clave": p.lower(), "respuesta_id": rid}).execute()
        return True
    except Exception as e:
        print(f"Error al guardar: {e}")
        return False

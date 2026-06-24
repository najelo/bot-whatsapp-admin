from auth_utils import get_supabase

def obtener_configuraciones():
    # Esta es la consulta que tu base de datos necesita
    try:
        return get_supabase().table("clientes").select("*, respuestas(*)").execute().data
    except Exception as e:
        print(f"Error en consulta: {e}")
        return []

def guardar_configuracion(palabras, contenido):
    try:
        supabase = get_supabase()
        res = supabase.table("respuestas").insert({"contenido": contenido}).execute()
        rid = res.data[0]['id']
        for p in [p.strip() for p in palabras.split(',')]:
            supabase.table("clientes").insert({"palabra_clave": p.lower(), "respuesta_id": rid}).execute()
        return True
    except: return False

from auth_utils import get_supabase

def obtener_configuraciones():
    """
    Trae los datos de 'clientes' uniendo la información de 'respuestas'.
    El 'respuestas(*)' es el JOIN que permite que app.py acceda a conf['respuestas'].
    """
    try:
        response = get_supabase().table("clientes").select("*, respuestas(*)").execute()
        return response.data
    except Exception as e:
        print(f"Error al obtener configuraciones: {e}")
        return []

def guardar_configuracion(palabra_clave, contenido):
    """
    Guarda los datos en dos pasos: primero en 'respuestas' y luego en 'clientes'
    para mantener la integridad relacional.
    """
    try:
        # 1. Primero creamos la respuesta y obtenemos su ID
        resp_response = get_supabase().table("respuestas").insert({
            "contenido": contenido
        }).execute()
        
        # Obtenemos el ID de la fila recién creada
        nueva_respuesta_id = resp_response.data[0]['id']
        
        # 2. Guardamos en 'clientes' usando el ID de la respuesta
        get_supabase().table("clientes").insert({
            "palabra_clave": palabra_clave,
            "respuesta_id": nueva_respuesta_id
        }).execute()
        
        return True
    except Exception as e:
        print(f"Error al guardar configuración: {e}")
        return False

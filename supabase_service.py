import os
from supabase import create_client, Client
from postgrest.exceptions import APIError

# 1. Conexión centralizada con Supabase (Usa tu archivo .env)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Error: Faltan las variables de entorno SUPABASE_URL o SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# 2. FUNCIÓN PARA ELIMINAR (La que necesitabas)
def eliminar_registro(id_registro: int, nombre_tabla: str):
    """Elimina una fila específica en Supabase usando su ID."""
    try:
        respuesta = supabase.table(nombre_tabla).delete().eq("id", id_registro).execute()
        return len(respuesta.data) > 0  # Devuelve True si borró algo, False si no
    except APIError as e:
        print(f"Error de Supabase al eliminar: {e.message}")
        return False

# 3. OTRAS FUNCIONES ÚTILES QUE PUEDES AGREGAR AQUÍ:

def obtener_todos_los_registros(nombre_tabla: str):
    """Trae todos los datos de una tabla para mostrarlos en la app."""
    try:
        respuesta = supabase.table(nombre_tabla).select("*").execute()
        return respuesta.data  # Devuelve una lista con tus filas
    except APIError as e:
        print(f"Error al leer datos: {e.message}")
        return []

def insertar_nuevo_registro(nombre_tabla: str, datos_a_guardar: dict):
    """Guarda un nuevo registro en la base de datos."""
    try:
        respuesta = supabase.table(nombre_tabla).insert(datos_a_guardar).execute()
        return respuesta.data
    except APIError as e:
        print(f"Error al insertar: {e.message}")
        return None

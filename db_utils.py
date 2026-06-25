import uuid
import streamlit as st
from auth_utils import get_supabase

def obtener_configuraciones():
    """
    Trae las palabras clave de la tabla 'clientes' junto con su relación 
    hacia la tabla 'respuestas' incluyendo el 'tipo_contenido'.
    """
    try:
        return get_supabase().table("clientes").select(
            "id, palabra_clave, respuesta_id, respuestas(id, contenido, tipo_contenido)"
        ).execute().data
    except Exception as e:
        print(f"Error al obtener configuraciones: {e}")
        return []

def subir_archivo_al_storage(archivo_bytes, nombre_archivo, bucket_name="recetarios-helado"):
    """
    Sube un archivo binario al bucket de Supabase Storage de manera correcta
    forzando la cabecera 'application/pdf' para evitar corrupciones.
    """
    try:
        supabase = get_supabase()
        nombre_unico = f"{uuid.uuid4()}_{nombre_archivo}"
        
        # Pasamos las opciones con el diccionario correcto que espera el SDK de Supabase
        supabase.storage.from_(bucket_name).upload(
            path=nombre_unico, 
            file=archivo_bytes,
            file_options={"content-type": "application/pdf"}
        )
        return supabase.storage.from_(bucket_name).get_public_url(nombre_unico)
    except Exception as e:
        print(f"Error al subir archivo al Storage: {e}")
        return None

def listar_archivos_storage(bucket_name="recetarios-helado"):
    """Lista los archivos PDF disponibles en el Storage."""
    try:
        lista = get_supabase().storage.from_(bucket_name).list()
        return [f["name"] for f in lista if f["name"].endswith(".pdf")]
    except Exception: 
        return []

def guardar_configuracion(palabras, contenido, tipo_contenido="texto"):
    """
    Guarda una respuesta especificando su tipo (texto, documento, multimedia, audio)
    Muestra el error real en la interfaz de Streamlit si la inserción falla.
    """
    try:
        supabase = get_supabase()
        
        # Alerta informativa temporal para confirmar que el código nuevo está corriendo
        st.toast(f"🔄 Procesando tipo: {tipo_contenido}...", icon="📥")
        
        # 1. Insertamos la respuesta con su respectivo tipo de contenido
        res = supabase.table("respuestas").insert({
            "contenido": contenido,
            "tipo_contenido": tipo_contenido
        }).execute()
        
        if not res.data:
            st.error("⚠️ Supabase procesó la solicitud pero devolvió un conjunto de datos vacío.")
            return False
            
        rid = res.data[0]['id']
        
        # 2. Procesamos e insertamos cada palabra clave por separado
        for p in [p.strip().lower() for p in palabras.split(',')]:
            if p: 
                supabase.table("clientes").insert({
                    "palabra_clave": p, 
                    "respuesta_id": rid  
                }).execute()
        return True
    except Exception as e:
        # Muestra el error real en pantalla si algo falla en el backend
        st.error(f"❌ Error interno de Supabase: {e}")
        return False

def eliminar_regla(cliente_id, respuesta_id):
    """Elimina una palabra clave de 'clientes' y su respuesta asociada de 'respuestas'."""
    try:
        supabase = get_supabase()
        supabase.table("clientes").delete().eq("id", cliente_id).execute()
        supabase.table("respuestas").delete().eq("id", respuesta_id).execute()
        return True
    except Exception as e:
        print(f"Error al eliminar regla: {e}")
        return False

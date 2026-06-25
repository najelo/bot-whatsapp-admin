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

def subir_archivo_al_storage(archivo, nombre_archivo, bucket_name="recetarios-helado"):
    """
    Sube cualquier archivo multimedia (PDF, Imagen, Video, Audio) detectando
    su extensión exacta para inyectar el Content-Type correcto en Supabase.
    Sostiene formatos de audio nativos de WhatsApp como .opus.
    """
    try:
        supabase = get_supabase()
        nombre_unico = f"{uuid.uuid4()}_{nombre_archivo}"
        
        # 1. Extraemos de forma segura los bytes del archivo según su origen
        if hasattr(archivo, "getvalue"):
            datos_binarios = archivo.getvalue()
        elif isinstance(archivo, bytes):
            datos_binarios = archivo
        else:
            datos_binarios = archivo.read()
            
        # 2. Diccionario extendido de mapeo dinámico para Content-Type
        ext = nombre_archivo.split('.')[-1].lower()
        
        mapeo_tipos = {
            # Documentos
            "pdf": "application/pdf",
            
            # Imágenes
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "webp": "image/webp",
            
            # Videos
            "mp4": "video/mp4",
            "3gp": "video/3gpp",
            
            # Audios y Notas de Voz Nativas (WhatsApp usa .opus / .ogg)
            "opus": "audio/ogg; codecs=opus",
            "ogg": "audio/ogg",
            "mp3": "audio/mpeg",
            "wav": "audio/wav",
            "m4a": "audio/x-m4a",
            "amr": "audio/amr"
        }
        
        # Si no reconoce la extensión, asigna un binario genérico seguro
        content_type_detectado = mapeo_tipos.get(ext, "application/octet-stream")
        
        # Definimos las propiedades de metadatos para Supabase
        opciones = {"content-type": content_type_detectado}
        
        # 3. Ejecutamos la carga binaria con su tipo multimedia correspondiente
        supabase.storage.from_(bucket_name).upload(
            path=nombre_unico, 
            file=datos_binarios,
            file_options=opciones
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
        
        # Alerta informativa en la interfaz
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

import streamlit as st
from auth_utils import get_supabase

def obtener_todos_los_flujos():
    try:
        supabase = get_supabase()
        res = supabase.table("flujos").select("*").execute()
        return res.data if res.data else []
    except Exception as e:
        st.error(f"❌ Error de conexión al leer flujos: {e}")
        return []

def crear_nuevo_flujo(nombre, palabra_clave):
    try:
        supabase = get_supabase()
        keyword_limpia = palabra_clave.lower().strip()
        
        # 1. Intentamos la inserción en la tabla flujos
        res_flujo = supabase.table("flujos").insert({
            "nombre": nombre,
            "palabra_clave": keyword_limpia
        }).execute()
        
        # Si Supabase responde vacío o sin datos
        if not res_flujo.data or len(res_flujo.data) == 0:
            st.error("⚠️ Supabase procesó la solicitud pero no devolvió el ID del flujo creado.")
            return False
            
        flujo_id = res_flujo.data[0]['id']
        
        # 2. Intentamos crear el nodo de inicio automático
        try:
            supabase.table("nodos_flujo").insert({
                "flujo_id": flujo_id,
                "tipo_nodo": "inicio",
                "configuracion": {"titulo": f"Disparador: {keyword_limpia}"},
                "posicion_x": 100.0,
                "posicion_y": 250.0
            }).execute()
        except Exception as e_nodo:
            st.error(f"💥 Se creó el flujo, pero falló la creación del nodo inicial: {e_nodo}")
            return False
        
        return True
    except Exception as e:
        # Esto romperá el misterio y pintará el error exacto en tu pantalla de Streamlit
        st.error(f"🛑 Error crítico en la base de datos: {e}")
        return False

def obtener_datos_lienzo(flujo_id):
    try:
        supabase = get_supabase()
        nodos = supabase.table("nodos_flujo").select("*").eq("flujo_id", flujo_id).execute().data
        conexiones = supabase.table("conexiones_nodos").select("*").eq("flujo_id", flujo_id).execute().data
        return nodos or [], conexiones or []
    except Exception as e:
        st.error(f"❌ Error al cargar el lienzo del flujo: {e}")
        return [], []

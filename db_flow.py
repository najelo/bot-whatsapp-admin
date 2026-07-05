import streamlit as st
from auth_utils import get_supabase

def obtener_todos_los_flujos():
    try:
        return get_supabase().table("flujos").select("*").execute().data
    except Exception as e:
        print(f"Error al obtener flujos: {e}")
        return []

def crear_nuevo_flujo(nombre, palabra_clave):
    try:
        supabase = get_supabase()
        # 1. Creamos el registro del flujo
        res_flujo = supabase.table("flujos").insert({
            "nombre": nombre,
            "palabra_clave": palabra_clave.lower().strip()
        }).execute()
        
        if not res_flujo.data:
            return False
            
        flujo_id = res_flujo.data[0]['id']
        
        # 2. Por defecto, le creamos su primer bloque automático: El nodo de Inicio
        supabase.table("nodos_flujo").insert({
            "flujo_id": flujo_id,
            "tipo_nodo": "inicio",
            "configuracion": {"titulo": f"Disparador: {palabra_clave}"},
            "posicion_x": 100.0,
            "posicion_y": 250.0
        }).execute()
        
        return True
    except Exception as e:
        print(f"Error al crear flujo: {e}")
        return False

def obtener_datos_lienzo(flujo_id):
    """Trae todos los nodos y conexiones de un flujo específico para dibujarlos"""
    try:
        supabase = get_supabase()
        nodos = supabase.table("nodos_flujo").select("*").eq("flujo_id", flujo_id).execute().data
        conexiones = supabase.table("conexiones_nodos").select("*").eq("flujo_id", flujo_id).execute().data
        return nodos or [], conexiones or []
    except Exception as e:
        print(f"Error al obtener datos del lienzo: {e}")
        return [], []

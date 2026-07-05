import streamlit as st
from auth_utils import get_supabase

def obtener_todos_los_flujos():
    try:
        supabase = get_supabase()
        res = supabase.table("flujos").select("*").execute()
        return res.data if res.data else []
    except Exception as e:
        print(f"Error al obtener flujos: {e}")
        return []

def crear_nuevo_flujo(nombre, palabra_clave):
    try:
        supabase = get_supabase()
        keyword_limpia = palabra_clave.lower().strip()
        
        # 1. Insertamos el flujo y pedimos explícitamente que devuelva la fila creada
        res_flujo = supabase.table("flujos").insert({
            "nombre": nombre,
            "palabra_clave": keyword_limpia
        }).execute()
        
        # Verificamos si Supabase retornó datos válidos
        if not res_flujo.data or len(res_flujo.data) == 0:
            print("Supabase no retornó datos al insertar el flujo.")
            return False
            
        flujo_id = res_flujo.data[0]['id']
        
        # 2. Creamos el nodo de Inicio automático asociado a ese flujo
        supabase.table("nodos_flujo").insert({
            "flujo_id": flujo_id,
            "tipo_nodo": "inicio",
            "configuracion": {"titulo": f"Disparador: {keyword_limpia}"},
            "posicion_x": 100.0,
            "posicion_y": 250.0
        }).execute()
        
        return True
    except Exception as e:
        # Esto imprimirá el error real en los logs de tu Streamlit Cloud para saber qué pasa exactamente
        print(f"ERROR REAL EN CREAR_NUEVO_FLUJO: {e}")
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

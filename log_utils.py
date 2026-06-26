import streamlit as st
from datetime import datetime

# 🛑 CONFIGURACIÓN DE PRUEBAS: Cambia a False cuando construyas la tabla en Supabase
MODO_MOCK = False 

def obtener_metricas_del_dia(supabase):
    if MODO_MOCK:
        return {"monto": "Bs. 3,320.00", "procesados": "5", "alertas": "0"}
    try:
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        query = supabase.table("historial_pagos").select("*").gte("created_at", f"{fecha_hoy}T00:00:00").execute()
        registros = query.data if query.data else []
        total_procesados = len(registros)
        aprobados = [r for r in registros if r.get("estado") == "aprobado"]
        alertas = [r for r in registros if r.get("estado") in ["alerta", "sospechoso", "error"]]
        monto_hoy = sum(float(r.get("monto", 0)) for r in aprobados)
        return {"monto": f"Bs. {monto_hoy:,.2f}", "procesados": str(total_procesados), "alertas": str(len(alertas))}
    except Exception as e:
        return {"monto": "Bs. 0.00", "procesados": "0", "alertas": "0"}

def obtener_todos_los_logs(supabase):
    if MODO_MOCK:
        return [
            {"created_at": "2026-06-26T14:23:10", "phone": "584121234567", "monto": 3300.0, "estado": "aprobado"},
            {"created_at": "2026-06-26T15:10:02", "phone": "584249876543", "monto": 20.0, "estado": "aprobado"},
            {"created_at": "2026-06-26T15:45:12", "phone": "584165554433", "monto": 0.0, "estado": "error"}, # <-- Limpiado aquí
            {"created_at": "2026-06-25T11:12:30", "phone": "584120001122", "monto": 10.0, "estado": "aprobado"},
            {"created_at": "2026-06-25T18:22:19", "phone": "584149998877", "monto": 3300.0, "estado": "alerta"},
        ]
    try:
   query = supabase.table("historial_pagos").select("*").order("created_at", descend=True).execute()
        return query.data if query.data else []
    except Exception as e:
        st.error(f"Error al cargar logs de Supabase: {e}")
        return []

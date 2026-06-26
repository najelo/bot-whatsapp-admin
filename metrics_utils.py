import os
from datetime import datetime
from auth_utils import get_supabase

def obtener_metricas_del_dia():
    """
    Consulta los registros de hoy en Supabase para calcular:
    1. El monto total verificado en Bs.
    2. La cantidad de capturas procesadas.
    3. Las alertas o fallas detectadas.
    """
    try:
        supabase = get_supabase()
        # Obtenemos la fecha de hoy en formato YYYY-MM-DD
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        
        # Consultamos los registros que fueron creados desde el inicio del día de hoy
        query = supabase.table("historial_pagos").select("*").gte("created_at", f"{fecha_hoy}T00:00:00").execute()
        registros = query.data if query.data else []
        
        total_procesados = len(registros)
        # Filtramos según el campo 'estado' que guarde tu bot (ej: aprobado / alerta)
        aprobados = [r for r in registros if r.get("estado") == "aprobado"]
        alertas = [r for r in registros if r.get("estado") in ["alerta", "sospechoso", "error"]]
        
        # Sumamos los montos de los pagos aprobados hoy
        monto_hoy = sum(float(r.get("monto", 0)) for r in aprobados)
        
        return {
            "monto": f"Bs.

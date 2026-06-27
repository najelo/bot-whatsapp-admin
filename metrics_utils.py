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
       fecha_hoy = datetime.now().strftime("%Y-%m-%d")
query = supabase.table("historial_pagos").select("*").gte("created_at", f"{fecha_hoy}T00:00:00").execute()

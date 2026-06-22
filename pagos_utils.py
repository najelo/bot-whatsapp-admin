from auth_utils import get_supabase

def obtener_configuracion_pagos():
    """Trae las reglas de aprobación (monto mínimo, número activo, etc.)."""
    try:
        supabase = get_supabase()
        response = supabase.table("configuracion_pago").select("*").execute()
        return response.data
    except Exception:
        return []

def guardar_regla_pago(telefono, identidad, monto_minimo):
    """Guarda los parámetros para la validación de pagos."""
    try:
        supabase = get_supabase()
        supabase.table("configuracion_pago").insert({
            "telefono_activo": telefono,
            "identidad_activa": identidad,
            "monto_minimo_aprobacion": monto_minimo
        }).execute()
        return True, "Reglas de pago actualizadas"
    except Exception as e:
        return False, str(e)

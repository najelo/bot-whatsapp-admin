from auth_utils import get_supabase

def obtener_configuracion_pagos():
    """Trae la lista de configuraciones de pago registradas."""
    try:
        return get_supabase().table("configuracion_pago").select("*").execute().data
    except Exception as e:
        print(f"Error al obtener pagos: {e}")
        return []

def guardar_contacto(cedula, telefono):
    """Registra un nuevo contacto de pago esperando validación."""
    try:
        get_supabase().table("configuracion_pago").insert({
            "cedula_esperada": cedula.strip(),
            "telefono_esperado": telefono.strip(),
            "activo": False
        }).execute()
        return True
    except Exception as e:
        print(f"Error al guardar contacto: {e}")
        return False

def activar_contacto(pago_id):
    """Activa un contacto de pago y desactiva los demás (o según tu lógica de negocio)."""
    try:
        supabase = get_supabase()
        # Opcional: Desactivar los demás si solo quieres uno activo a la vez
        supabase.table("configuracion_pago").update({"activo": False}).neq("id", pago_id).execute()
        
        # Activar el seleccionado
        supabase.table("configuracion_pago").update({"activo": True}).eq("id", pago_id).execute()
        return True
    except Exception as e:
        print(f"Error al activar contacto: {e}")
        return False

import bcrypt

def verificar_login(username, password_input):
    # 1. Buscar el usuario en Supabase
    usuario = supabase.table("usuarios").select("*").eq("username", username).execute()
    
    if not usuario.data:
        return False, "Usuario no encontrado"

    hash_guardado = usuario.data[0]["password_hash"].encode('utf-8')
    
    # 2. Comparar el hash con la contraseña ingresada
    if bcrypt.checkpw(password_input.encode('utf-8'), hash_guardado):
        return True, "Login exitoso"
    else:
        return False, "Contraseña incorrecta"

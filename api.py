from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pagos_utils
import auth_utils
import log_utils

app = FastAPI()

# Permitir que la web acceda a la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción, cambia esto por tu URL de Vercel
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/pagos")
def get_pagos():
    return pagos_utils.obtener_resumen_pagos()

@app.get("/api/auth/status")
def check_auth():
    return {"status": "autenticado"} # Aquí llamas a tu lógica de login.py

# ... puedes ir agregando todos los endpoints que necesites

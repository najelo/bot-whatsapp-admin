from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pagos_utils  # Tus archivos actuales
import auth_utils

app = FastAPI()

# Esto permite que tu web en /web pueda hablar con este archivo en la raíz
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/pagos")
def get_pagos():
    return pagos_utils.obtener_resumen_pagos()

@app.get("/api/metricas")
def get_metricas():
    return {"status": "ok", "data": "tus datos de metricas aquí"}

# Aquí agregarás todos tus endpoints conforme los necesites

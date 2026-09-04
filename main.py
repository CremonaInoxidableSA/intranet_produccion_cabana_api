from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import pallets, cargar_pallet, detalles_pallet, editar_pallet

app = FastAPI(
    title="API Produccion Cabaña - Gestión de Pallets",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pallets.router)
app.include_router(cargar_pallet.router)
app.include_router(detalles_pallet.router)
app.include_router(editar_pallet.router)

@app.get("/")
def root():
    return {
        "mensaje": "API produccion cabaña funcionando"
    }

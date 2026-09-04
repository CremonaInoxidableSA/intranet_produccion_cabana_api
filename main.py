from fastapi import FastAPI
from routes import pallets


app = FastAPI(
    title="API Produccion Cabaña - Gestión de Pallets",
    version="1.0.0"
)


app.include_router(pallets.router)


@app.get("/")
def root():
    return {
        "mensaje": "API produccion cabaña funcionando"
    }
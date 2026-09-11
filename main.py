from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.movimientos import cargar_producto, retirar_producto, mover_producto
from routes.productos import crear_producto, lista_productos
from routes.pallets import crear_pallet, detalles_pallet, lista_pallets

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

app.include_router(crear_pallet.router)
app.include_router(lista_pallets.router)
app.include_router(detalles_pallet.router)

app.include_router(crear_producto.router)
app.include_router(lista_productos.router)

app.include_router(cargar_producto.router)
app.include_router(retirar_producto.router)
app.include_router(mover_producto.router)

@app.get("/")
def root():
    return {
        "mensaje": "API produccion cabaña funcionando"
    }

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sql.database import get_db
from sql.models import Productos
from sql.schemas import ProductoResponse
from typing import List, Any

router = APIRouter(prefix="/lista_productos", tags=["Productos"])

@router.get("/", response_model=List[ProductoResponse])
def listar_productos(db: Session = Depends(get_db)) -> List[ProductoResponse]:
    productos: list[Any] = db.query(Productos).all()
    resultado: List[ProductoResponse] = []

    for p in productos:
        producto_response = ProductoResponse(
            id_producto=p.id_producto,
            nombre=str(p.nombre),
            empresa=str(p.empresa),
            codigo=str(p.codigo),
            tipo=str(p.tipo)
        )

        resultado.append(producto_response)

    return resultado

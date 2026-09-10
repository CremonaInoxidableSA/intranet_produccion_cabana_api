from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from sql.database import get_db
from sql.models import Productos
from sql.schemas import ProductoCreate, ProductoResponse

router = APIRouter(
    prefix="/crear_producto",
    tags=["Productos"]
)

@router.post("/", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
def crear_nuevo_producto(
    producto_data: ProductoCreate,
    db: Session = Depends(get_db)
):
    existing_product = db.query(Productos).filter(
        Productos.codigo == producto_data.codigo
    ).first()

    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un producto con el código {producto_data.codigo}"
        )

    nuevo_producto = Productos(
        nombre=producto_data.nombre,
        codigo=producto_data.codigo,
        empresa=producto_data.empresa,
        tipo=producto_data.tipo
    )

    try:
        db.add(nuevo_producto)
        db.commit()
        db.refresh(nuevo_producto)
        return nuevo_producto
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear el producto. Verifica que el código sea único."
        )
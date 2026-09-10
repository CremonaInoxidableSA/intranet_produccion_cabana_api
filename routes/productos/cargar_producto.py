from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from sql.database import get_db
from sql.models import Productos
from sql.schemas import ProductoCreate, ProductoResponse

router = APIRouter(
    prefix="/cargar_producto",
    tags=["Productos"]
)

@router.post("/", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
def cargar_producto_al_pallet(
    producto_data: ProductoCreate,
    db: Session = Depends(get_db)
):
    existing_producto = db.query(Productos).filter(
        Productos.codigo == producto_data.codigo
    ).first()

    if not existing_producto:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El producto con código {producto_data.codigo} no existe"
        )

    nuevo_registro = Productos(
        id_producto=existing_producto.id_producto,
        codigo=producto_data.codigo,
    )

    try:
        db.add(nuevo_registro)
        db.commit()
        db.refresh(nuevo_registro)
        return nuevo_registro
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al cargar el producto."
        )
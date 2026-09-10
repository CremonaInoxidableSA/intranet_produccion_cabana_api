from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from sql.database import get_db
from sql.models import Pallets
from sql.schemas import PalletCreate, PalletResponse

router = APIRouter(
    prefix="/crear_pallet",
    tags=["Pallets"]
)

@router.post("/", response_model=PalletResponse, status_code=status.HTTP_201_CREATED)
def crear_nuevo_pallet(
    pallet_data: PalletCreate,
    db: Session = Depends(get_db)
):
    # Verificar si ya existe un pallet con ese código
    existing_pallet = db.query(Pallets).filter(
        Pallets.codigo == pallet_data.codigo
    ).first()
    
    if existing_pallet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un pallet con el código {pallet_data.codigo}"
        )
    
    # Crear el nuevo pallet
    nuevo_pallet = Pallets(
        codigo=pallet_data.codigo,
        tipo=pallet_data.tipo,
        fecha_compra=pallet_data.fecha_compra,
        estado=pallet_data.estado
    )
    
    try:
        db.add(nuevo_pallet)
        db.commit()
        db.refresh(nuevo_pallet)
        return nuevo_pallet
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear el pallet. Verifica que el código sea único."
        )
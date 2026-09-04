from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from sql.database import get_db
from sql.models import Pallet
from sql.schemas import PalletCreate, PalletResponse

router = APIRouter(
    prefix="/cargar_pallet",
    tags=["Pallets"]
)

@router.post("/", response_model=PalletResponse, status_code=status.HTTP_201_CREATED)
def cargar_nuevo_pallet(
    pallet_data: PalletCreate,
    db: Session = Depends(get_db)
):
    existing_pallet = db.query(Pallet).filter(
        Pallet.codigo_pallet == pallet_data.codigo_pallet
    ).first()
    
    if existing_pallet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un pallet con el código {pallet_data.codigo_pallet}"
        )
    
    nuevo_pallet = Pallet(
        codigo_pallet=pallet_data.codigo_pallet,
        producto=None,
        lote=None,
        fecha_carga=None,
        cantidad=None,
        estado=False
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
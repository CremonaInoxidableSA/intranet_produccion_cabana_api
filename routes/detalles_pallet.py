from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from sql.database import get_db
from sql.models import Pallet
from sql.schemas import PalletResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/detalles_pallet",
    tags=["Pallets"]
)

@router.get("/{pallet_id}", response_model=PalletResponse)
def obtener_pallet_por_id(
    pallet_id: int,
    db: Session = Depends(get_db)
):
    pallet = db.query(Pallet).filter(Pallet.id_pallet == pallet_id).first()
    
    if not pallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró un pallet con ID {pallet_id}"
        )
    
    logger.info(f"Obteniendo detalles del pallet ID: {pallet_id}")
    return pallet

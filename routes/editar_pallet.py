from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import cast
import logging

from sql.database import get_db
from sql.models import Pallet
from sql.schemas import PalletUpdate, PalletUpdateWithRetiro, PalletResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/editar_pallet",
    tags=["Pallets"]
)


@router.put("/{pallet_id}", response_model=PalletResponse)
def editar_pallet(
    pallet_id: int,
    pallet_data: PalletUpdate,
    db: Session = Depends(get_db)
):
    logger.info(f"Editando pallet ID: {pallet_id}")
    
    pallet = db.query(Pallet).filter(Pallet.id_pallet == pallet_id).first()
    
    if not pallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró un pallet con ID {pallet_id}"
        )
    
    producto = cast(str | None, pallet.producto)
    cantidad = cast(int | None, pallet.cantidad)
    tiene_producto = producto is not None and cantidad is not None and cantidad > 0
    
    if not tiene_producto:
        logger.info(f"Pallet sin producto - Cargando datos iniciales")
        
        if not all([pallet_data.producto, pallet_data.lote, pallet_data.fecha_carga, pallet_data.cantidad]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Para cargar un pallet se necesitan: producto, lote, fecha_carga y cantidad"
            )
        
        setattr(pallet, "producto", pallet_data.producto)
        setattr(pallet, "lote", pallet_data.lote)
        setattr(pallet, "fecha_carga", pallet_data.fecha_carga)
        setattr(pallet, "cantidad", pallet_data.cantidad)
        setattr(pallet, "estado", True)
        
    else:
        logger.info(f"Pallet con producto - No se pueden cambiar datos")
        
        if (pallet_data.producto is not None or 
            pallet_data.lote is not None or 
            pallet_data.fecha_carga is not None):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este pallet ya tiene producto asignado. Use el endpoint /retirar para modificar la cantidad."
            )
    
    try:
        db.commit()
        db.refresh(pallet)
        logger.info(f"Pallet ID {pallet_id} actualizado exitosamente")
        return pallet
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al editar pallet: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al editar el pallet. Verifica que el lote sea único."
        )


@router.put("/{pallet_id}/retirar", response_model=PalletResponse)
def retirar_cantidad_pallet(
    pallet_id: int,
    retiro_data: PalletUpdateWithRetiro,
    db: Session = Depends(get_db)
):
    logger.info(f"Retirando cantidad del pallet ID: {pallet_id}")
    
    pallet = db.query(Pallet).filter(Pallet.id_pallet == pallet_id).first()
    
    if not pallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró un pallet con ID {pallet_id}"
        )
    
    producto = cast(str | None, pallet.producto)
    cantidad_actual = cast(int | None, pallet.cantidad)
    
    if producto is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El pallet no tiene producto asignado. No se puede retirar cantidad."
        )
    
    if cantidad_actual is None or cantidad_actual <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El pallet no tiene cantidad disponible. Cantidad actual: {cantidad_actual}"
        )
    
    if retiro_data.cantidad_retirar > cantidad_actual:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cantidad inválida. Solo hay {cantidad_actual} unidades disponibles, no se puede retirar {retiro_data.cantidad_retirar}."
        )
    
    nueva_cantidad = cantidad_actual - retiro_data.cantidad_retirar
    
    if nueva_cantidad == 0:
        logger.info(f"Pallet ID {pallet_id} - Cantidad llegó a cero. Limpiando datos del pallet.")
        setattr(pallet, "producto", None)
        setattr(pallet, "lote", None)
        setattr(pallet, "fecha_carga", None)
        setattr(pallet, "cantidad", None)
        setattr(pallet, "estado", False)
    else:
        setattr(pallet, "cantidad", nueva_cantidad)
    
    try:
        db.commit()
        db.refresh(pallet)
        logger.info(f"Retiro exitoso. Nueva cantidad: {pallet.cantidad}")
        return pallet
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error al retirar cantidad: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al retirar la cantidad."
        )
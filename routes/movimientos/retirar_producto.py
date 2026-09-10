from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import update
from typing import cast

from sql.database import get_db
from sql.models import Pallets, Productos, PalletsProductos, Movimientos, CargasDescargas
from sql.schemas import RetiroPalletRequest, MovimientoResponse

router = APIRouter(
    prefix="/retirar_producto",
    tags=["Productos"]
)

@router.post("/{id_pallet}/{id_producto}", response_model=MovimientoResponse, status_code=status.HTTP_200_OK)
def retirar_producto_del_pallet(
    id_pallet: int,
    id_producto: int,
    datos_retiro: RetiroPalletRequest,
    db: Session = Depends(get_db)
):
    pallet = db.query(Pallets).filter(Pallets.id_pallet == id_pallet).first()
    if not pallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El pallet con ID {id_pallet} no existe"
        )

    producto = db.query(Productos).filter(Productos.id_producto == id_producto).first()
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El producto con ID {id_producto} no existe"
        )

    pallet_producto = db.query(PalletsProductos).filter(
        PalletsProductos.id_pallet == id_pallet,
        PalletsProductos.id_producto == id_producto
    ).first()

    if not pallet_producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El producto {id_producto} no se encuentra en el pallet {id_pallet}"
        )

    cantidad_actual = cast(int, pallet_producto.cantidad_producto)
    cantidad_retirar = datos_retiro.cantidad_retirar

    if cantidad_retirar > cantidad_actual:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No hay suficiente cantidad. Disponible: {cantidad_actual}, Solicitado: {cantidad_retirar}"
        )

    cantidad_resultante = cantidad_actual - cantidad_retirar

    try:
        if cantidad_resultante <= 0:
            db.delete(pallet_producto)
        else:
            db.execute(
                update(PalletsProductos).where(
                    (PalletsProductos.id_pallet == id_pallet) &
                    (PalletsProductos.id_producto == id_producto)
                ).values(cantidad_producto=cantidad_resultante)
            )

        registro_descarga = CargasDescargas(
            tipo='descarga',
            id_pallet=id_pallet,
            id_producto=id_producto,
            cantidad_anterior=cantidad_actual,
            cantidad_modificada=-cantidad_retirar,
            peso_kg=str(datos_retiro.peso_kg) if datos_retiro.peso_kg is not None else None,
            motivo=datos_retiro.motivo,
            usuario=datos_retiro.usuario
        )
        db.add(registro_descarga)

        movimiento = Movimientos(
            tipo='ajuste',
            id_pallet_producto_origen=pallet_producto.id_pallet_producto,
            id_producto=id_producto,
            cantidad_anterior_origen=cantidad_actual,
            cantidad_anterior_destino=0,
            cantidad_modificada=-cantidad_retirar,
            motivo=datos_retiro.motivo,
            usuario=datos_retiro.usuario
        )

        db.add(movimiento)
        db.commit()

        if cantidad_resultante <= 0:
            return {"mensaje": "Producto retirado y eliminado del pallet"}

        return {"mensaje": "Movimiento registrado"}

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al procesar el retiro. Verifica los datos ingresados."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

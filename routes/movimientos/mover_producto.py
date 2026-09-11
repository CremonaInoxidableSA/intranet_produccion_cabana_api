from datetime import date
from typing import Any, Optional, cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from sql.database import get_db
from sql.models import Movimientos, Pallets, PalletsProductos
from sql.schemas import MoverProductoRequest, MoverProductoResponse


router = APIRouter(
	prefix="/mover_producto",
	tags=["Movimientos"]
)


def _buscar_registro_destino(
	db: Session,
	id_pallet_destino: int,
	id_producto: int,
	lote: Optional[str],
	fecha_vencimiento: Optional[date],
):
	query = db.query(PalletsProductos).filter(
		PalletsProductos.id_pallet == id_pallet_destino,
		PalletsProductos.id_producto == id_producto,
	)

	if lote is None:
		query = query.filter(PalletsProductos.lote.is_(None))
	else:
		query = query.filter(PalletsProductos.lote == lote)

	if fecha_vencimiento is None:
		query = query.filter(PalletsProductos.fecha_vencimiento.is_(None))
	else:
		query = query.filter(PalletsProductos.fecha_vencimiento == fecha_vencimiento)

	return query.first()


@router.post("/", response_model=MoverProductoResponse, status_code=status.HTTP_200_OK)
def mover_producto_entre_pallets(
	payload: MoverProductoRequest,
	db: Session = Depends(get_db)
) -> MoverProductoResponse:
	registro_origen = db.query(PalletsProductos).filter(
		PalletsProductos.id_pallet_producto == payload.id_pallet_producto_origen
	).first()

	if not registro_origen:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"No existe el producto del pallet origen con id {payload.id_pallet_producto_origen}"
		)

	registro_origen_db = cast(Any, registro_origen)
	if registro_origen_db.cantidad_producto < payload.cantidad_producto:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="La cantidad a mover no puede ser mayor a la cantidad disponible"
		)

	pallet_origen = db.query(Pallets).filter(Pallets.id_pallet == registro_origen_db.id_pallet).first()
	if not pallet_origen:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"No existe el pallet origen con id {registro_origen_db.id_pallet}"
		)

	pallet_destino = db.query(Pallets).filter(Pallets.id_pallet == payload.id_pallet_destino).first()
	if not pallet_destino:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"No existe el pallet destino con id {payload.id_pallet_destino}"
		)

	if registro_origen_db.id_pallet == payload.id_pallet_destino:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="El pallet origen y destino no pueden ser el mismo"
		)

	fecha_operacion = payload.actualizado
	producto_id = int(registro_origen_db.id_producto)
	id_pallet_origen = int(registro_origen_db.id_pallet)
	lote = cast(Optional[str], registro_origen_db.lote)
	fecha_vencimiento = cast(Optional[date], registro_origen_db.fecha_vencimiento)
	cantidad_anterior_origen = int(registro_origen_db.cantidad_producto)

	try:
		cantidad_restante_origen = cantidad_anterior_origen - payload.cantidad_producto
		if cantidad_restante_origen == 0:
			db.delete(registro_origen_db)
		else:
			registro_origen_db.cantidad_producto = cantidad_restante_origen

		registro_destino = _buscar_registro_destino(
			db=db,
			id_pallet_destino=payload.id_pallet_destino,
			id_producto=producto_id,
			lote=lote,
			fecha_vencimiento=fecha_vencimiento,
		)

		cantidad_anterior_destino = 0
		if registro_destino:
			registro_destino_db = cast(Any, registro_destino)
			cantidad_anterior_destino = int(registro_destino_db.cantidad_producto)
			registro_destino_db.cantidad_producto = cantidad_anterior_destino + payload.cantidad_producto
			id_pallet_producto_destino = int(registro_destino_db.id_pallet_producto)
		else:
			nuevo_destino = PalletsProductos(
				id_pallet=payload.id_pallet_destino,
				id_producto=producto_id,
				cantidad_producto=payload.cantidad_producto,
				lote=lote,
				fecha_vencimiento=fecha_vencimiento,
				fecha_ingreso=fecha_operacion.date()
			)
			db.add(nuevo_destino)
			db.flush()
			nuevo_destino_db = cast(Any, nuevo_destino)
			id_pallet_producto_destino = int(nuevo_destino_db.id_pallet_producto)

		pallet_origen_db = cast(Any, pallet_origen)
		pallet_destino_db = cast(Any, pallet_destino)
		pallet_origen_db.actualizado = fecha_operacion
		pallet_destino_db.actualizado = fecha_operacion

		quedan_productos_en_origen = db.query(PalletsProductos.id_pallet_producto).filter(
			PalletsProductos.id_pallet == id_pallet_origen
		).first()
		pallet_origen_db.estado = 1 if quedan_productos_en_origen else 0

		quedan_productos_en_destino = db.query(PalletsProductos.id_pallet_producto).filter(
			PalletsProductos.id_pallet == pallet_destino_db.id_pallet
		).first()
		pallet_destino_db.estado = 1 if quedan_productos_en_destino else 0

		movimiento = Movimientos(
			tipo="traslado",
			id_pallet_producto_origen=registro_origen_db.id_pallet_producto,
			id_pallet_producto_destino=id_pallet_producto_destino,
			id_producto=producto_id,
			cantidad_anterior_origen=cantidad_anterior_origen,
			cantidad_anterior_destino=cantidad_anterior_destino,
			cantidad_modificada=payload.cantidad_producto,
			motivo=payload.motivo,
			usuario=payload.usuario,
			fecha_movimiento=fecha_operacion
		)
		db.add(movimiento)
		db.commit()

		return MoverProductoResponse(mensaje="Producto movido correctamente")

	except Exception:
		db.rollback()
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="El producto no se pudo mover correctamente"
		)
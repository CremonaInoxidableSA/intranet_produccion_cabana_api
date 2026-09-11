from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, cast

from routes.registros.registrar_carga_descarga import registrar_carga_descarga
from sql.database import get_db
from sql.models import Pallets, PalletsProductos
from sql.schemas import RetiroProductoRequest, RetiroProductoResponse


router = APIRouter(
	prefix="/retirar_producto",
	tags=["Movimientos"]
)


@router.post("/", response_model=RetiroProductoResponse, status_code=status.HTTP_200_OK)
def retirar_producto_del_pallet(
	payload: RetiroProductoRequest,
	db: Session = Depends(get_db)
) -> RetiroProductoResponse:
	registro = db.query(PalletsProductos).filter(
		PalletsProductos.id_pallet_producto == payload.id_pallet_producto
	).first()

	if not registro:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"No existe el producto del pallet con id {payload.id_pallet_producto}"
		)

	registro_db = cast(Any, registro)
	pallet = db.query(Pallets).filter(Pallets.id_pallet == registro_db.id_pallet).first()
	if not pallet:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"No existe el pallet con id {registro_db.id_pallet}"
		)

	cantidad_actual = int(registro_db.cantidad_producto)
	if payload.cantidad_producto > cantidad_actual:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="La cantidad a retirar no puede ser mayor a la cantidad disponible"
		)

	fecha_operacion = payload.actualizado

	try:
		cantidad_restante = cantidad_actual - payload.cantidad_producto

		if cantidad_restante == 0:
			db.delete(registro_db)
		else:
			registro_db.cantidad_producto = cantidad_restante

		pallet_db = cast(Any, pallet)
		pallet_db.actualizado = fecha_operacion

		si_quedan_productos = db.query(PalletsProductos.id_pallet_producto).filter(
			PalletsProductos.id_pallet == registro_db.id_pallet
		).first()

		if not si_quedan_productos:
			pallet_db.estado = 0

		registrar_carga_descarga(
			db=db,
			tipo="descarga",
			id_pallet=int(registro_db.id_pallet),
			id_producto=int(registro_db.id_producto),
			cantidad_anterior=cantidad_actual,
			cantidad_modificada=payload.cantidad_producto,
			usuario=payload.usuario,
			fecha_operacion=fecha_operacion,
			motivo=payload.motivo,
			peso_kg=payload.peso_kg,
		)
		db.commit()

		return RetiroProductoResponse(mensaje="Producto retirado correctamente")

	except Exception:
		db.rollback()
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="El producto no se pudo retirar correctamente"
		)

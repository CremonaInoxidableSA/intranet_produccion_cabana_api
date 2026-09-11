from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, cast

from routes.registros.registrar_carga_descarga import registrar_carga_descarga
from sql.database import get_db
from sql.models import Pallets, PalletsProductos, Productos
from sql.schemas import CargaProductoRequest, CargaProductoResponse


router = APIRouter(
	prefix="/cargar_producto",
	tags=["Movimientos"]
)
@router.post("/", response_model=CargaProductoResponse, status_code=status.HTTP_201_CREATED)
def cargar_producto_en_pallet(
	payload: CargaProductoRequest,
	db: Session = Depends(get_db)
)-> CargaProductoResponse:
	pallet = db.query(Pallets).filter(Pallets.id_pallet == payload.id_pallet).first()
	if not pallet:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"No existe el pallet con id {payload.id_pallet}"
		)

	producto = db.query(Productos).filter(Productos.id_producto == payload.id_producto).first()
	if not producto:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"No existe el producto con id {payload.id_producto}"
		)

	query_existente = db.query(PalletsProductos).filter(
		PalletsProductos.id_pallet == payload.id_pallet,
		PalletsProductos.id_producto == payload.id_producto
	)

	if payload.lote is None:
		query_existente = query_existente.filter(PalletsProductos.lote.is_(None))
	else:
		query_existente = query_existente.filter(PalletsProductos.lote == payload.lote)

	if payload.fecha_vencimiento is None:
		query_existente = query_existente.filter(PalletsProductos.fecha_vencimiento.is_(None))
	else:
		query_existente = query_existente.filter(PalletsProductos.fecha_vencimiento == payload.fecha_vencimiento)

	registro_existente = query_existente.first()
	cantidad_anterior = 0
	fecha_operacion = payload.actualizado

	try:
		if registro_existente:
			registro_existente_db = cast(Any, registro_existente)
			cantidad_anterior = registro_existente_db.cantidad_producto
			registro_existente_db.cantidad_producto = cantidad_anterior + payload.cantidad_producto
		else:
			nuevo_registro = PalletsProductos(
				id_pallet=payload.id_pallet,
				id_producto=payload.id_producto,
				cantidad_producto=payload.cantidad_producto,
				lote=payload.lote,
				fecha_vencimiento=payload.fecha_vencimiento,
				fecha_ingreso=payload.fecha_ingreso
			)
			db.add(nuevo_registro)
			db.flush()

		# Si el pallet estaba inactivo (vacío), se activa y se actualiza su timestamp.
		pallet_db = cast(Any, pallet)
		if pallet_db.estado == 0:
			pallet_db.estado = 1
		pallet_db.actualizado = fecha_operacion

		registrar_carga_descarga(
			db=db,
			tipo="carga",
			id_pallet=payload.id_pallet,
			id_producto=payload.id_producto,
			cantidad_anterior=cantidad_anterior,
			cantidad_modificada=payload.cantidad_producto,
			usuario=payload.usuario,
			fecha_operacion=fecha_operacion,
			motivo=payload.motivo,
		)

		db.commit()

		return CargaProductoResponse(mensaje="Producto cargado correctamente")

	except Exception:
		db.rollback()
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="El producto no se pudo cargar correctamente"
		)

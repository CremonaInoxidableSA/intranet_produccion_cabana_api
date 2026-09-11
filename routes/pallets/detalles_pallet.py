from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
import logging
from typing import cast, List
from datetime import datetime, date

from sql.database import get_db
from sql.models import Pallets, Movimientos
from sql.schemas import PalletDetalleResponse, ProductoDetalleResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/detalles_pallet",
    tags=["Pallets"]
)

@router.get("/{pallet_id}", response_model=PalletDetalleResponse)
def obtener_pallet_por_id(
    pallet_id: int,
    db: Session = Depends(get_db)
) -> PalletDetalleResponse:
    pallet = db.query(Pallets).filter(Pallets.id_pallet == pallet_id).first()

    if not pallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró un pallet con ID {pallet_id}"
        )

    logger.info(f"Obteniendo detalles del pallet ID: {pallet_id}")

    contenido: List[ProductoDetalleResponse] = []
    productos = pallet.pallet_productos

    proximo_vencimiento: date | None = None
    fechas_vencimiento: List[date] = []

    for pallet_producto in productos:
        producto = pallet_producto.producto
        id_pallet_producto = cast(int, pallet_producto.id_pallet_producto)
        producto_codigo = cast(str, producto.codigo)
        producto_nombre = cast(str, producto.nombre)
        producto_empresa = cast(str, producto.empresa)
        producto_tipo = cast(str, producto.tipo)
        producto_lote = cast(str | None, pallet_producto.lote)
        producto_fecha_vencimiento = cast(date | None, pallet_producto.fecha_vencimiento)
        producto_fecha_ingreso = cast(date, pallet_producto.fecha_ingreso)
        cantidad = cast(int, pallet_producto.cantidad_producto)

        if producto_fecha_vencimiento is not None:
            fechas_vencimiento.append(producto_fecha_vencimiento)

        contenido.append(ProductoDetalleResponse(
            id_pallet_producto=id_pallet_producto,
            codigo=producto_codigo,
            nombre=producto_nombre,
            empresa=producto_empresa,
            tipo=producto_tipo,
            cantidad=cantidad,
            lote=producto_lote or "",
            fecha_vencimiento=producto_fecha_vencimiento or date.today(),
            fecha_ingreso=producto_fecha_ingreso
        ))

    if fechas_vencimiento:
        proximo_vencimiento = min(fechas_vencimiento)

    ids_pallet_productos = [p.id_pallet_producto for p in productos if p.id_pallet_producto is not None]
    movimiento_reciente = None
    if ids_pallet_productos:
        movimiento_reciente = db.query(Movimientos).filter(
            or_(
                Movimientos.id_pallet_producto_origen.in_(ids_pallet_productos),
                Movimientos.id_pallet_producto_destino.in_(ids_pallet_productos)
            )
        ).order_by(desc(Movimientos.fecha_movimiento)).first()

    ultima_actividad: datetime | None = None
    ultima_actividad_usuario: str | None = None
    if movimiento_reciente:
        ultima_actividad = cast(datetime, movimiento_reciente.fecha_movimiento)
        ultima_actividad_usuario = cast(str, movimiento_reciente.usuario)

    respuesta = PalletDetalleResponse(
        id_pallet=cast(int, pallet.id_pallet),
        codigo=cast(str, pallet.codigo),
        tipo=cast(str, pallet.tipo),
        fecha_compra=cast(date | None, pallet.fecha_compra),
        estado=cast(bool, pallet.estado),
        contenido=contenido,
        proximo_vencimiento=proximo_vencimiento,
        ultima_actividad=ultima_actividad,
        ultima_actividad_usuario=ultima_actividad_usuario
    )

    return respuesta

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from sql.models import CargasDescargas


def registrar_carga_descarga(
	db: Session,
	tipo: str,
	id_pallet: int,
	id_producto: int,
	cantidad_anterior: int,
	cantidad_modificada: int,
	usuario: str,
	fecha_operacion: datetime,
	motivo: Optional[str] = None,
	peso_kg: Optional[Decimal] = None,
) -> None:
	registro = CargasDescargas(
		tipo=tipo,
		id_pallet=id_pallet,
		id_producto=id_producto,
		cantidad_anterior=cantidad_anterior,
		cantidad_modificada=cantidad_modificada,
		peso_kg=None if peso_kg is None else str(peso_kg),
		motivo=motivo,
		usuario=usuario,
		fecha_carga_descarga=fecha_operacion,
	)
	db.add(registro)

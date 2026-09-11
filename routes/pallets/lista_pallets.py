from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sql.database import get_db
from sql.models import Pallets
from sql.schemas import PalletResponse, PalletContenidoResponse
from typing import List, Optional
from datetime import date

router = APIRouter(prefix="/lista_pallets", tags=["Pallets"])

@router.get("/", response_model=List[PalletResponse])
def listar_pallets(db: Session = Depends(get_db)) -> List[PalletResponse]:
    pallets = db.query(Pallets).all()

    resultado: List[PalletResponse] = []

    for pallet in pallets:
        productos = pallet.pallet_productos
        contenido: List[PalletContenidoResponse] = []

        lotes: List[str] = []
        for p in productos:
            if p.lote and p.lote not in lotes:
                lotes.append(p.lote)

            contenido.append(PalletContenidoResponse(
                id_pallet_producto=int(p.id_pallet_producto),
                id_producto=int(p.id_producto),
                cantidad=int(p.cantidad_producto),
                lote=str(p.lote or ""),
                fecha_vencimiento=p.fecha_vencimiento,
            ))

        proximo_vencimiento: Optional[date] = None
        if productos:
            fechas = [p.fecha_vencimiento for p in productos if p.fecha_vencimiento is not None]
            if fechas:
                proximo_vencimiento = min(fechas)

        pallet_response = PalletResponse(
            id_pallet=int(pallet.id_pallet),
            codigo=str(pallet.codigo),
            estado=int(pallet.estado),
            lote=lotes,
            contenido=contenido,
            proximo_vencimiento=proximo_vencimiento,
        )

        resultado.append(pallet_response)

    return resultado

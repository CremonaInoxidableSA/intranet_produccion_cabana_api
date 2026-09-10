from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sql.database import get_db
from sql.models import Pallets
from sql.schemas import PalletResponse
from typing import List, Optional, Any
from datetime import date

router = APIRouter(prefix="/lista_pallets", tags=["Pallets"])

@router.get("/", response_model=List[PalletResponse])
def listar_pallets(db: Session = Depends(get_db)) -> List[PalletResponse]:
    pallets: list[Any] = db.query(Pallets).all()

    resultado: List[PalletResponse] = []

    for pallet in pallets:
        productos = pallet.pallet_productos

        lotes: List[str] = []
        for p in productos:
            if p.lote and p.lote not in lotes:
                lotes.append(p.lote)

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
            proximo_vencimiento=proximo_vencimiento,
        )

        resultado.append(pallet_response)

    return resultado

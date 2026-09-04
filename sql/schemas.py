from pydantic import BaseModel
from typing import Optional
from datetime import date

class PalletCreate(BaseModel):
    codigo_pallet: str

class PalletResponse(BaseModel):
    id_pallet: int
    codigo_pallet: str
    producto: Optional[str] = None
    lote: Optional[str] = None
    fecha_carga: Optional[date] = None
    cantidad: Optional[int] = None
    estado: bool

    class Config:
        from_attributes = True
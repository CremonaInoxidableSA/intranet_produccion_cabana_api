from pydantic import BaseModel, Field, field_validator
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

class PalletUpdate(BaseModel):
    """Para actualizar un pallet sin producto (cargar)"""
    producto: Optional[str] = None
    lote: Optional[str] = None
    fecha_carga: Optional[date] = None
    cantidad: Optional[int] = Field(None, ge=0, description="Cantidad debe ser mayor o igual a 0")

class PalletUpdateWithRetiro(BaseModel):
    """Para actualizar cantidad (retiro) en un pallet con producto"""
    cantidad_retirar: int = Field(..., gt=0, description="Cantidad a retirar debe ser mayor a 0")
    
    @field_validator('cantidad_retirar')
    @classmethod
    def validar_cantidad_retirar(cls, v: int) -> int:
        if v <= 0:
            raise ValueError('La cantidad a retirar debe ser mayor a 0')
        return v

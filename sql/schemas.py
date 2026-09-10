from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, ForwardRef, Dict
from datetime import date, datetime
from decimal import Decimal

# ============== Forward References ==============
# Definimos referencias adelantadas para evitar dependencias circulares
PalletResponseRef = ForwardRef('PalletResponse')
ProductoResponseRef = ForwardRef('ProductoResponse')


# ============== Producto Schemas ==============
class ProductoBase(BaseModel):
    nombre: str = Field(..., max_length=150)
    codigo: str = Field(..., max_length=50)
    empresa: str = Field(..., max_length=100)
    tipo: str = Field(..., max_length=50)

class ProductoCreate(ProductoBase):
    pass

class ProductoResponse(ProductoBase):
    id_producto: int
    codigo: str
    empresa: str
    tipo: str
    
    class Config:
        from_attributes = True


# ============== Pallets Schemas ==============
class PalletBase(BaseModel):
    codigo: str = Field(..., max_length=50)
    tipo: str = Field(..., max_length=50)
    fecha_compra: Optional[date] = None
    estado: int = Field(default=1, ge=0, le=1)

class PalletCreate(PalletBase):
    pass

class PalletUpdate(BaseModel):
    tipo: Optional[str] = Field(None, max_length=50)
    fecha_compra: Optional[date] = None
    estado: Optional[int] = Field(None, ge=0, le=1)

class PalletResponse(BaseModel):
    id_pallet: int
    codigo: str
    estado: int
    lote: List[str] = []
    proximo_vencimiento: Optional[date] = None
    
    class Config:
        from_attributes = True


# ============== PalletProducto Schemas ==============
class PalletProductoBase(BaseModel):
    id_pallet: int
    id_producto: int
    cantidad_actual: int = Field(default=0, ge=0)

class PalletProductoCreate(PalletProductoBase):
    pass

class PalletProductoUpdate(BaseModel):
    cantidad_actual: int = Field(..., ge=0)

class PalletProductoResponse(BaseModel):
    id_pallet_producto: int
    id_pallet: int
    id_producto: int
    cantidad_actual: int
    fecha_ingreso: datetime
    pallet: Optional[PalletResponse] = None
    producto: Optional[ProductoResponse] = None
    
    class Config:
        from_attributes = True


# ============== Movimiento Schemas ==============
class MovimientoBase(BaseModel):
    id_pallet_origen: Optional[int] = None
    id_pallet_destino: Optional[int] = None
    id_producto: int
    tipo_movimiento: str = Field(..., pattern="^(carga|retiro|mov_interno|ajuste|lectura)$")
    cantidad_movida: int = Field(..., gt=0)
    cantidad_anterior: int = Field(..., ge=0)
    peso_kg: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    motivo: Optional[str] = None
    usuario: str = Field(..., max_length=50)

class MovimientoCreate(MovimientoBase):
    pass


# ============== Detalle Pallets Schemas ==============
class ProductoDetalleResponse(BaseModel):
    """Producto con cantidad para mostrar en detalles del pallet"""
    id_producto: int
    nombre: str
    cantidad: int
    lote: str
    fecha_vencimiento: date


class PalletDetalleResponse(BaseModel):
    """Respuesta detallada del pallet con todos los productos"""
    id_pallet: int
    codigo: str
    tipo: str
    fecha_compra: Optional[date] = None
    estado: bool
    contenido: Dict[str, ProductoDetalleResponse]
    proximo_vencimiento: Optional[date] = None
    ultima_actividad: Optional[datetime] = None
    ultima_actividad_usuario: Optional[str] = None

    class Config:
        from_attributes = True

class MovimientoResponse(BaseModel):
    mensaje: str = "Movimiento registrado"
    
    class Config:
        from_attributes = True


# ============== Pallets con Productos (Respuesta Completa) ==============
class PalletWithProductsResponse(BaseModel):
    id_pallet: int
    codigo: str
    tipo: str
    fecha_compra: Optional[date] = None
    estado: bool
    productos: List[PalletProductoResponse] = []
    
    class Config:
        from_attributes = True


# ============== Operaciones de Carga y Retiro ==============
class CargaPalletRequest(BaseModel):
    """Para cargar producto en un pallet"""
    id_producto: int
    cantidad: int = Field(..., gt=0, description="Cantidad a cargar debe ser mayor a 0")
    usuario: str = Field(..., max_length=50)
    peso_kg: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    motivo: Optional[str] = None
    
    @field_validator('cantidad')
    @classmethod
    def validar_cantidad(cls, v: int) -> int:
        if v <= 0:
            raise ValueError('La cantidad debe ser mayor a 0')
        return v

class RetiroPalletRequest(BaseModel):
    """Para retirar producto de un pallet"""
    cantidad_retirar: int = Field(..., gt=0, description="Cantidad a retirar debe ser mayor a 0")
    usuario: str = Field(..., max_length=50)
    peso_kg: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    motivo: Optional[str] = None
    
    @field_validator('cantidad_retirar')
    @classmethod
    def validar_cantidad_retirar(cls, v: int) -> int:
        if v <= 0:
            raise ValueError('La cantidad a retirar debe ser mayor a 0')
        return v

class MovimientoInternoRequest(BaseModel):
    id_pallet_origen: int
    id_pallet_destino: int
    id_producto: int
    cantidad: int = Field(..., gt=0)
    usuario: str = Field(..., max_length=50)
    peso_kg: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    motivo: Optional[str] = None
    
    @field_validator('cantidad')
    @classmethod
    def validar_cantidad(cls, v: int) -> int:
        if v <= 0:
            raise ValueError('La cantidad debe ser mayor a 0')
        return v


PalletResponse.model_rebuild()
ProductoResponse.model_rebuild()
PalletProductoResponse.model_rebuild()
MovimientoResponse.model_rebuild()
PalletWithProductsResponse.model_rebuild()

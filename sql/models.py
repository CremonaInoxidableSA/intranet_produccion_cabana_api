from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Pallets(Base):
    __tablename__ = "Pallets"

    id_pallet = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False)
    tipo = Column(String(50), nullable=False)
    fecha_compra = Column(Date, nullable=False)
    estado = Column(Integer, nullable=False, default=1)
    actualizado = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)

    pallet_productos = relationship("PalletsProductos", back_populates="pallet", cascade="all, delete-orphan")


class Productos(Base):
    __tablename__ = "Productos"

    id_producto = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    codigo = Column(String(50), unique=True, nullable=False)
    empresa = Column(String(100), nullable=False)
    tipo = Column(String(50), nullable=False)

    pallet_productos = relationship("PalletsProductos", back_populates="producto")
    movimientos = relationship("Movimientos", back_populates="producto")


class PalletsProductos(Base):
    __tablename__ = "Pallets_Productos"

    id_pallet_producto = Column(Integer, primary_key=True, index=True)
    id_pallet = Column(Integer, ForeignKey("Pallets.id_pallet", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    id_producto = Column(Integer, ForeignKey("Productos.id_producto", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    cantidad_producto = Column(Integer, nullable=False, default=0)
    lote = Column(String(50), nullable=True)
    fecha_vencimiento = Column(Date, nullable=True)
    fecha_ingreso = Column(Date, nullable=False)
    actualizado = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)

    pallet = relationship("Pallets", back_populates="pallet_productos")
    producto = relationship("Productos", back_populates="pallet_productos")
    movimientos_origen = relationship("Movimientos", foreign_keys="Movimientos.id_pallet_producto_origen", back_populates="pallet_producto_origen")
    movimientos_destino = relationship("Movimientos", foreign_keys="Movimientos.id_pallet_producto_destino", back_populates="pallet_producto_destino")

    __table_args__ = (
        CheckConstraint('cantidad_producto >= 0', name='check_cantidad_producto_positive'),
    )


class CargasDescargas(Base):
    __tablename__ = "Cargas_Descargas"

    id_carga_descarga = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(20), nullable=False)
    id_pallet = Column(Integer, ForeignKey("Pallets.id_pallet", onupdate="CASCADE"), nullable=False)
    id_producto = Column(Integer, ForeignKey("Productos.id_producto", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    cantidad_anterior = Column(Integer, nullable=False)
    cantidad_modificada = Column(Integer, nullable=False)
    peso_kg = Column(String(50), nullable=True)
    motivo = Column(String(255), nullable=True)
    usuario = Column(String(100), nullable=False)
    fecha_carga_descarga = Column(DateTime, default=func.current_timestamp(), nullable=False)

    pallet = relationship("Pallets")
    producto = relationship("Productos")

    __table_args__ = (
        CheckConstraint("tipo IN ('carga', 'descarga')", name='check_tipo_carga_descarga'),
    )


class Movimientos(Base):
    __tablename__ = "Movimientos"

    id_movimiento = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(20), nullable=False)
    id_pallet_producto_origen = Column(Integer, ForeignKey("Pallets_Productos.id_pallet_producto", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    id_pallet_producto_destino = Column(Integer, ForeignKey("Pallets_Productos.id_pallet_producto", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    id_producto = Column(Integer, ForeignKey("Productos.id_producto", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    cantidad_anterior_origen = Column(Integer, nullable=False, default=0)
    cantidad_anterior_destino = Column(Integer, nullable=False, default=0)
    cantidad_modificada = Column(Integer, nullable=False)
    motivo = Column(String(255), nullable=True)
    usuario = Column(String(100), nullable=False)
    fecha_movimiento = Column(DateTime, default=func.current_timestamp(), nullable=False)

    pallet_producto_origen = relationship("PalletsProductos", foreign_keys=[id_pallet_producto_origen], back_populates="movimientos_origen")
    pallet_producto_destino = relationship("PalletsProductos", foreign_keys=[id_pallet_producto_destino], back_populates="movimientos_destino")
    producto = relationship("Productos", back_populates="movimientos")

    __table_args__ = (
        CheckConstraint("tipo IN ('ajuste', 'traslado')", name='check_tipo_movimiento'),
    )
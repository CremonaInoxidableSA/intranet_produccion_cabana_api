from sqlalchemy import Column, Integer, String, Date

from .database import Base


class Pallet(Base):
    __tablename__ = "pallet"

    id_pallet = Column(Integer, primary_key=True, index=True)
    codigo_pallet = Column(String(255), unique=True, nullable=False)
    producto = Column(String(255), nullable=True)
    lote = Column(String(255), unique=True, nullable=True)
    fecha_carga = Column(Date, nullable=True)
    cantidad = Column(Integer, nullable=True)
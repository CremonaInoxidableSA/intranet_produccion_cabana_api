from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from sql.database import get_db
from sql.models import Pallet


router = APIRouter(
    prefix="/lista-pallets",
    tags=["Pallets"]
)


@router.get("/")
def obtener_pallets(db: Session = Depends(get_db)):

    pallets = db.query(Pallet).all()

    return pallets
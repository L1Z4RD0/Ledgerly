from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import IngresoExtra, Mes

router = APIRouter()

@router.get("/{mes_id}")
def get_extras(mes_id: int, db: Session = Depends(get_db)):
    return db.query(IngresoExtra).filter(IngresoExtra.mes_id == mes_id).all()

@router.post("/{mes_id}")
def crear_extra(mes_id: int, descripcion: str, monto: float, fecha: str, db: Session = Depends(get_db)):
    if monto <= 0:
        raise HTTPException(status_code=400, detail="El monto debe ser positivo")
    
    mes = db.query(Mes).filter(Mes.id == mes_id).first()
    if not mes:
        raise HTTPException(status_code=404, detail="Mes no encontrado")
    nuevo = IngresoExtra(
        mes_id=mes_id,
        descripcion=descripcion,
        monto=monto,
        fecha=fecha
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.put("/{extra_id}")
def actualizar_extra(extra_id: int, descripcion: str, monto: float, fecha: str, db: Session = Depends(get_db)):
    extra = db.query(IngresoExtra).filter(IngresoExtra.id == extra_id).first()
    if not extra:
        raise HTTPException(status_code=404, detail="Ingreso extra no encontrado")
    extra.descripcion = descripcion
    extra.monto = monto
    extra.fecha = fecha
    db.commit()
    db.refresh(extra)
    return extra

@router.delete("/{extra_id}")
def eliminar_extra(extra_id: int, db: Session = Depends(get_db)):
    extra = db.query(IngresoExtra).filter(IngresoExtra.id == extra_id).first()
    if not extra:
        raise HTTPException(status_code=404, detail="Ingreso extra no encontrado")
    db.delete(extra)
    db.commit()
    return {"mensaje": "Ingreso extra eliminado"}

@router.get("/{mes_id}/total")
def total_extras(mes_id: int, db: Session = Depends(get_db)):
    extras = db.query(IngresoExtra).filter(IngresoExtra.mes_id == mes_id).all()
    total = sum(e.monto for e in extras)
    return {"mes_id": mes_id, "total": total}
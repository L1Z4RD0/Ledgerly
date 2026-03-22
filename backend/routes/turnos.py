from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Semana, Mes

router = APIRouter()

@router.get("/{mes_id}")
def get_semanas(mes_id: int, db: Session = Depends(get_db)):
    return db.query(Semana).filter(Semana.mes_id == mes_id).all()

@router.post("/{mes_id}")
def crear_semana(mes_id: int, numero_semana: int, turnos: int, valor_turno: float = 16000, db: Session = Depends(get_db)):
    mes = db.query(Mes).filter(Mes.id == mes_id).first()
    if not mes:
        raise HTTPException(status_code=404, detail="Mes no encontrado")
    existe = db.query(Semana).filter(
        Semana.mes_id == mes_id,
        Semana.numero_semana == numero_semana
    ).first()
    if existe:
        existe.turnos = turnos
        existe.valor_turno = valor_turno
        db.commit()
        db.refresh(existe)
        return existe
    nueva = Semana(
        mes_id=mes_id,
        numero_semana=numero_semana,
        turnos=turnos,
        valor_turno=valor_turno
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.put("/{semana_id}")
def actualizar_semana(semana_id: int, turnos: int, valor_turno: float = 16000, db: Session = Depends(get_db)):
    semana = db.query(Semana).filter(Semana.id == semana_id).first()
    if not semana:
        raise HTTPException(status_code=404, detail="Semana no encontrada")
    semana.turnos = turnos
    semana.valor_turno = valor_turno
    db.commit()
    db.refresh(semana)
    return semana

@router.delete("/{semana_id}")
def eliminar_semana(semana_id: int, db: Session = Depends(get_db)):
    semana = db.query(Semana).filter(Semana.id == semana_id).first()
    if not semana:
        raise HTTPException(status_code=404, detail="Semana no encontrada")
    db.delete(semana)
    db.commit()
    return {"mensaje": "Semana eliminada"}
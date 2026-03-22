from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Deuda, PagoDeuda, Mes
import datetime

router = APIRouter()

@router.get("/")
def get_deudas(db: Session = Depends(get_db)):
    return db.query(Deuda).all()

@router.get("/activas")
def get_deudas_activas(db: Session = Depends(get_db)):
    return db.query(Deuda).filter(Deuda.activa == True).all()

@router.post("/")
def crear_deuda(nombre: str, monto_total: float, cuota: float, tipo: str = "fijo", db: Session = Depends(get_db)):
    if tipo not in ["fijo", "porcentaje"]:
        raise HTTPException(status_code=400, detail="Tipo debe ser 'fijo' o 'porcentaje'")
    nueva = Deuda(nombre=nombre, monto_total=monto_total, cuota=cuota, tipo=tipo)
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.put("/{deuda_id}")
def actualizar_deuda(deuda_id: int, nombre: str, monto_total: float, cuota: float, tipo: str, db: Session = Depends(get_db)):
    deuda = db.query(Deuda).filter(Deuda.id == deuda_id).first()
    if not deuda:
        raise HTTPException(status_code=404, detail="Deuda no encontrada")
    deuda.nombre = nombre
    deuda.monto_total = monto_total
    deuda.cuota = cuota
    deuda.tipo = tipo
    db.commit()
    db.refresh(deuda)
    return deuda

@router.post("/{deuda_id}/pagar")
def registrar_pago(deuda_id: int, mes_id: int, monto: float, db: Session = Depends(get_db)):
    deuda = db.query(Deuda).filter(Deuda.id == deuda_id).first()
    if not deuda:
        raise HTTPException(status_code=404, detail="Deuda no encontrada")
    mes = db.query(Mes).filter(Mes.id == mes_id).first()
    if not mes:
        raise HTTPException(status_code=404, detail="Mes no encontrado")
    pago = PagoDeuda(
        mes_id=mes_id,
        deuda_id=deuda_id,
        monto=monto,
        fecha=str(datetime.date.today())
    )
    db.add(pago)
    deuda.monto_pagado += monto
    if deuda.monto_pagado >= deuda.monto_total:
        deuda.monto_pagado = deuda.monto_total
        deuda.activa = False
    db.commit()
    db.refresh(deuda)
    return deuda

@router.get("/{mes_id}/pagos")
def get_pagos_mes(mes_id: int, db: Session = Depends(get_db)):
    pagos = db.query(PagoDeuda).filter(PagoDeuda.mes_id == mes_id).all()
    resultado = []
    for p in pagos:
        deuda = db.query(Deuda).filter(Deuda.id == p.deuda_id).first()
        resultado.append({
            "id": p.id,
            "deuda_id": p.deuda_id,
            "nombre_deuda": deuda.nombre if deuda else "—",
            "monto": p.monto,
            "fecha": p.fecha
        })
    return resultado

@router.put("/{deuda_id}/desactivar")
def desactivar_deuda(deuda_id: int, db: Session = Depends(get_db)):
    deuda = db.query(Deuda).filter(Deuda.id == deuda_id).first()
    if not deuda:
        raise HTTPException(status_code=404, detail="Deuda no encontrada")
    deuda.activa = False
    db.commit()
    db.refresh(deuda)
    return deuda

@router.delete("/{deuda_id}")
def eliminar_deuda(deuda_id: int, db: Session = Depends(get_db)):
    deuda = db.query(Deuda).filter(Deuda.id == deuda_id).first()
    if not deuda:
        raise HTTPException(status_code=404, detail="Deuda no encontrada")
    db.delete(deuda)
    db.commit()
    return {"mensaje": "Deuda eliminada"}
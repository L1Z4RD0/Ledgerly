from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Deuda, PagoDeuda, Mes, IngresoExtra, Gasto, AporteAhorro
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
    if monto_total <= 0:
        raise HTTPException(status_code=400, detail="El monto total debe ser positivo")
    if cuota <= 0:
        raise HTTPException(status_code=400, detail="La cuota debe ser positiva")
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

    if monto <= 0:
        raise HTTPException(status_code=400, detail="El monto debe ser mayor a 0")

    saldo_anterior = mes.saldo_anterior or 0
    extras = db.query(IngresoExtra).filter(IngresoExtra.mes_id == mes_id).all()
    total_extras = sum(e.monto for e in extras)
    gastos = db.query(Gasto).filter(Gasto.mes_id == mes_id).all()
    total_gastos = sum(g.monto for g in gastos)
    pagos = db.query(PagoDeuda).filter(PagoDeuda.mes_id == mes_id).all()
    total_pagos = sum(p.monto for p in pagos)
    aportes = db.query(AporteAhorro).filter(AporteAhorro.mes_id == mes_id).all()
    total_aportes = sum(a.monto for a in aportes)

    saldo_disponible = saldo_anterior + total_extras - total_gastos - total_pagos - total_aportes

    if saldo_disponible <= 0:
        raise HTTPException(status_code=400, detail="Sin saldo disponible. Agrega un ingreso extra primero.")
    if monto > saldo_disponible:
        raise HTTPException(status_code=400, detail=f"Saldo insuficiente. Disponible: {saldo_disponible}")

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
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Gasto, Mes, IngresoExtra, PagoDeuda, AporteAhorro

router = APIRouter()

@router.get("/{mes_id}")
def get_gastos(mes_id: int, db: Session = Depends(get_db)):
    return db.query(Gasto).filter(Gasto.mes_id == mes_id).all()

@router.post("/{mes_id}")
def crear_gasto(mes_id: int, nombre: str, categoria: str, monto: float, fecha: str, db: Session = Depends(get_db)):
    if monto <= 0:
        raise HTTPException(status_code=400, detail="El monto debe ser positivo")
    
    mes = db.query(Mes).filter(Mes.id == mes_id).first()
    if not mes:
        raise HTTPException(status_code=404, detail="Mes no encontrado")

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

    nuevo = Gasto(mes_id=mes_id, nombre=nombre, categoria=categoria, monto=monto, fecha=fecha)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo
@router.put("/{gasto_id}")
def actualizar_gasto(gasto_id: int, nombre: str, categoria: str, monto: float, fecha: str, db: Session = Depends(get_db)):
    gasto = db.query(Gasto).filter(Gasto.id == gasto_id).first()
    if not gasto:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    gasto.nombre = nombre
    gasto.categoria = categoria
    gasto.monto = monto
    gasto.fecha = fecha
    db.commit()
    db.refresh(gasto)
    return gasto

@router.delete("/{gasto_id}")
def eliminar_gasto(gasto_id: int, db: Session = Depends(get_db)):
    gasto = db.query(Gasto).filter(Gasto.id == gasto_id).first()
    if not gasto:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    db.delete(gasto)
    db.commit()
    return {"mensaje": "Gasto eliminado"}

@router.get("/{mes_id}/por-categoria")
def gastos_por_categoria(mes_id: int, db: Session = Depends(get_db)):
    gastos = db.query(Gasto).filter(Gasto.mes_id == mes_id).all()
    categorias = {}
    for g in gastos:
        if g.categoria not in categorias:
            categorias[g.categoria] = 0
        categorias[g.categoria] += g.monto
    return categorias
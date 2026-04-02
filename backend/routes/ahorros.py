from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Ahorro, AporteAhorro, Mes, IngresoExtra, Gasto, PagoDeuda
import datetime

router = APIRouter()

@router.get("/")
def get_ahorros(db: Session = Depends(get_db)):
    return db.query(Ahorro).all()

@router.get("/activos")
def get_ahorros_activos(db: Session = Depends(get_db)):
    return db.query(Ahorro).filter(Ahorro.activo == True).all()

@router.post("/")
def crear_ahorro(nombre: str, descripcion: str, monto_meta: float = None, cuota: float = None, tipo: str = "fijo", db: Session = Depends(get_db)):
    if tipo not in ["fijo", "porcentaje"]:
        raise HTTPException(status_code=400, detail="Tipo debe ser 'fijo' o 'porcentaje'")
    if monto_meta is None and cuota is None:
        raise HTTPException(status_code=400, detail="Debe proporcionar al menos 'monto_meta' o 'cuota'")
    fecha_inicio = str(datetime.date.today())
    nuevo = Ahorro(nombre=nombre, descripcion=descripcion, monto_meta=monto_meta if monto_meta and monto_meta > 0 else None, cuota=cuota or 0, tipo=tipo, fecha_inicio=fecha_inicio)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.put("/{ahorro_id}")
def actualizar_ahorro(ahorro_id: int, nombre: str, descripcion: str, monto_meta: float, cuota: float, tipo: str, db: Session = Depends(get_db)):
    ahorro = db.query(Ahorro).filter(Ahorro.id == ahorro_id).first()
    if not ahorro:
        raise HTTPException(status_code=404, detail="Ahorro no encontrado")
    ahorro.nombre = nombre
    ahorro.descripcion = descripcion
    ahorro.monto_meta = monto_meta
    ahorro.cuota = cuota
    ahorro.tipo = tipo
    db.commit()
    db.refresh(ahorro)
    return ahorro

@router.post("/{ahorro_id}/aportar")
def registrar_aporte(ahorro_id: int, mes_id: int, monto: float, db: Session = Depends(get_db)):
    ahorro = db.query(Ahorro).filter(Ahorro.id == ahorro_id).first()
    if not ahorro:
        raise HTTPException(status_code=404, detail="Ahorro no encontrado")
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

    if monto > 0:
        if saldo_disponible <= 0:
            raise HTTPException(status_code=400, detail="Sin saldo disponible. Agrega un ingreso extra primero.")
        if monto > saldo_disponible:
            raise HTTPException(status_code=400, detail=f"Saldo insuficiente. Disponible: {saldo_disponible}")

    aporte = AporteAhorro(
        mes_id=mes_id,
        ahorro_id=ahorro_id,
        monto=monto,
        fecha=str(datetime.date.today())
    )
    db.add(aporte)
    ahorro.monto_actual += monto
    
    # Solo marcar como inactivo si tiene meta y la alcanza
    if ahorro.monto_meta and ahorro.monto_actual >= ahorro.monto_meta:
        ahorro.monto_actual = ahorro.monto_meta
        ahorro.activo = False
    # Si no tiene meta, nunca se desactiva automáticamente
    
    db.commit()
    db.refresh(ahorro)
    return ahorro

@router.get("/{mes_id}/aportes")
def get_aportes_mes(mes_id: int, db: Session = Depends(get_db)):
    aportes = db.query(AporteAhorro).filter(AporteAhorro.mes_id == mes_id).all()
    resultado = []
    for a in aportes:
        ahorro = db.query(Ahorro).filter(Ahorro.id == a.ahorro_id).first()
        resultado.append({
            "id": a.id,
            "ahorro_id": a.ahorro_id,
            "nombre_ahorro": ahorro.nombre if ahorro else "—",
            "monto": a.monto,
            "fecha": a.fecha
        })
    return resultado

@router.put("/{ahorro_id}/desactivar")
def desactivar_ahorro(ahorro_id: int, db: Session = Depends(get_db)):
    ahorro = db.query(Ahorro).filter(Ahorro.id == ahorro_id).first()
    if not ahorro:
        raise HTTPException(status_code=404, detail="Ahorro no encontrado")
    ahorro.activo = False
    db.commit()
    db.refresh(ahorro)
    return ahorro

@router.delete("/{ahorro_id}")
def eliminar_ahorro(ahorro_id: int, db: Session = Depends(get_db)):
    ahorro = db.query(Ahorro).filter(Ahorro.id == ahorro_id).first()
    if not ahorro:
        raise HTTPException(status_code=404, detail="Ahorro no encontrado")
    db.delete(ahorro)
    db.commit()
    return {"mensaje": "Ahorro eliminado"}

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Mes, Semana, Gasto, IngresoExtra, PagoDeuda

router = APIRouter()

AFP = 0.1046
FONASA = 0.07

@router.get("/")
def get_meses(db: Session = Depends(get_db)):
    return db.query(Mes).all()

@router.post("/")
def crear_mes(anio: int, mes: int, db: Session = Depends(get_db)):
    existe = db.query(Mes).filter(Mes.anio == anio, Mes.mes == mes).first()
    if existe:
        raise HTTPException(status_code=400, detail="Ese mes ya existe")

    anterior_anio = anio if mes > 1 else anio - 1
    anterior_mes_num = mes - 1 if mes > 1 else 12
    mes_anterior = db.query(Mes).filter(
        Mes.anio == anterior_anio,
        Mes.mes == anterior_mes_num
    ).first()

    saldo_inicial = 0
    if mes_anterior and mes_anterior.sueldo_real is not None:
        extras = db.query(IngresoExtra).filter(IngresoExtra.mes_id == mes_anterior.id).all()
        total_extras = sum(e.monto for e in extras)
        gastos = db.query(Gasto).filter(Gasto.mes_id == mes_anterior.id).all()
        total_gastos = sum(g.monto for g in gastos)
        pagos = db.query(PagoDeuda).filter(PagoDeuda.mes_id == mes_anterior.id).all()
        total_pagos = sum(p.monto for p in pagos)
        saldo_anterior_anterior = mes_anterior.saldo_anterior or 0
        saldo_inicial = mes_anterior.sueldo_real + saldo_anterior_anterior + total_extras - total_gastos - total_pagos

    nuevo = Mes(anio=anio, mes=mes, saldo_anterior=saldo_inicial)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.get("/{mes_id}/resumen")
def get_resumen(mes_id: int, db: Session = Depends(get_db)):
    mes = db.query(Mes).filter(Mes.id == mes_id).first()
    if not mes:
        raise HTTPException(status_code=404, detail="Mes no encontrado")

    semanas = db.query(Semana).filter(Semana.mes_id == mes_id).all()
    bruto = sum(s.turnos * s.valor_turno for s in semanas)
    descuento_afp = round(bruto * AFP)
    descuento_fonasa = round(bruto * FONASA)
    neto_estimado = bruto - descuento_afp - descuento_fonasa

    extras = db.query(IngresoExtra).filter(IngresoExtra.mes_id == mes_id).all()
    total_extras = sum(e.monto for e in extras)

    gastos = db.query(Gasto).filter(Gasto.mes_id == mes_id).all()
    total_gastos = sum(g.monto for g in gastos)

    pagos = db.query(PagoDeuda).filter(PagoDeuda.mes_id == mes_id).all()
    total_pagos_deuda = sum(p.monto for p in pagos)

    saldo_anterior = mes.saldo_anterior or 0
    mes_cerrado = mes.sueldo_real is not None

    # Saldo disponible real = lo que hay en el bolsillo ahora
    # Durante el mes = saldo anterior + extras − gastos − pagos deuda
    saldo_disponible = saldo_anterior + total_extras - total_gastos - total_pagos_deuda

    if mes_cerrado:
        # Al cerrar el mes se suma el liquido recibido
        saldo_libre = mes.sueldo_real + saldo_anterior + total_extras - total_gastos - total_pagos_deuda
    else:
        saldo_libre = None

    return {
        "mes_id": mes_id,
        "anio": mes.anio,
        "mes": mes.mes,
        "bruto": bruto,
        "descuento_afp": descuento_afp,
        "descuento_fonasa": descuento_fonasa,
        "neto_estimado": neto_estimado,
        "total_extras": total_extras,
        "total_gastos": total_gastos,
        "total_pagos_deuda": total_pagos_deuda,
        "saldo_anterior": saldo_anterior,
        "saldo_disponible": saldo_disponible,
        "mes_cerrado": mes_cerrado,
        "sueldo_real": mes.sueldo_real,
        "saldo_libre": saldo_libre,
        "diferencia_bruto": round(mes.sueldo_real - neto_estimado) if mes.sueldo_real else None
    }

@router.put("/{mes_id}/cerrar")
def cerrar_mes(mes_id: int, liquido: float, bruto_real: float = None, db: Session = Depends(get_db)):
    mes = db.query(Mes).filter(Mes.id == mes_id).first()
    if not mes:
        raise HTTPException(status_code=404, detail="Mes no encontrado")

    extras = db.query(IngresoExtra).filter(IngresoExtra.mes_id == mes_id).all()
    total_extras = sum(e.monto for e in extras)

    gastos = db.query(Gasto).filter(Gasto.mes_id == mes_id).all()
    total_gastos = sum(g.monto for g in gastos)

    pagos = db.query(PagoDeuda).filter(PagoDeuda.mes_id == mes_id).all()
    total_pagos_deuda = sum(p.monto for p in pagos)

    saldo_anterior = mes.saldo_anterior or 0
    saldo_libre = liquido + saldo_anterior + total_extras - total_gastos - total_pagos_deuda

    mes.sueldo_real = liquido
    if bruto_real:
        mes.notas = f"bruto_real:{bruto_real}"

    db.commit()

    siguiente_anio = mes.anio if mes.mes < 12 else mes.anio + 1
    siguiente_mes_num = mes.mes + 1 if mes.mes < 12 else 1
    mes_siguiente = db.query(Mes).filter(
        Mes.anio == siguiente_anio,
        Mes.mes == siguiente_mes_num
    ).first()

    if mes_siguiente:
        mes_siguiente.saldo_anterior = saldo_libre
        db.commit()

    db.refresh(mes)
    return {"mensaje": "Mes cerrado", "saldo_libre": saldo_libre, "saldo_traspasado": saldo_libre if mes_siguiente else None}
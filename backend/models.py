from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Mes(Base):
    __tablename__ = "meses"
    id = Column(Integer, primary_key=True, index=True)
    anio = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)
    sueldo_real = Column(Float, nullable=True)
    saldo_anterior = Column(Float, nullable=True, default=0)
    notas = Column(String, nullable=True)

    semanas = relationship("Semana", back_populates="mes", cascade="all, delete")
    gastos = relationship("Gasto", back_populates="mes", cascade="all, delete")
    ingresos_extra = relationship("IngresoExtra", back_populates="mes", cascade="all, delete")
    pagos_deuda = relationship("PagoDeuda", back_populates="mes", cascade="all, delete")


class Semana(Base):
    __tablename__ = "semanas"
    id = Column(Integer, primary_key=True, index=True)
    mes_id = Column(Integer, ForeignKey("meses.id"), nullable=False)
    numero_semana = Column(Integer, nullable=False)
    turnos = Column(Integer, nullable=False, default=0)
    valor_turno = Column(Float, nullable=False, default=16000)

    mes = relationship("Mes", back_populates="semanas")


class Gasto(Base):
    __tablename__ = "gastos"
    id = Column(Integer, primary_key=True, index=True)
    mes_id = Column(Integer, ForeignKey("meses.id"), nullable=False)
    nombre = Column(String, nullable=False)
    categoria = Column(String, nullable=False, default="General")
    monto = Column(Float, nullable=False)
    fecha = Column(String, nullable=False)

    mes = relationship("Mes", back_populates="gastos")


class IngresoExtra(Base):
    __tablename__ = "ingresos_extra"
    id = Column(Integer, primary_key=True, index=True)
    mes_id = Column(Integer, ForeignKey("meses.id"), nullable=False)
    descripcion = Column(String, nullable=False)
    monto = Column(Float, nullable=False)
    fecha = Column(String, nullable=False)

    mes = relationship("Mes", back_populates="ingresos_extra")


class Deuda(Base):
    __tablename__ = "deudas"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    monto_total = Column(Float, nullable=False)
    monto_pagado = Column(Float, nullable=False, default=0)
    cuota = Column(Float, nullable=False)
    tipo = Column(String, nullable=False, default="fijo")
    activa = Column(Boolean, nullable=False, default=True)

    pagos = relationship("PagoDeuda", back_populates="deuda", cascade="all, delete")


class PagoDeuda(Base):
    __tablename__ = "pagos_deuda"
    id = Column(Integer, primary_key=True, index=True)
    mes_id = Column(Integer, ForeignKey("meses.id"), nullable=False)
    deuda_id = Column(Integer, ForeignKey("deudas.id"), nullable=False)
    monto = Column(Float, nullable=False)
    fecha = Column(String, nullable=False)

    mes = relationship("Mes", back_populates="pagos_deuda")
    deuda = relationship("Deuda", back_populates="pagos")
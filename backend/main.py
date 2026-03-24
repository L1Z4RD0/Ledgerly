from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes import turnos, gastos, deudas, extras, meses, ahorros

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ledgerly API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(meses.router, prefix="/meses", tags=["meses"])
app.include_router(turnos.router, prefix="/turnos", tags=["turnos"])
app.include_router(gastos.router, prefix="/gastos", tags=["gastos"])
app.include_router(deudas.router, prefix="/deudas", tags=["deudas"])
app.include_router(extras.router, prefix="/extras", tags=["extras"])
app.include_router(ahorros.router, prefix="/ahorros", tags=["ahorros"])

@app.get("/")
def root():
    return {"mensaje": "Ledgerly API funcionando"}
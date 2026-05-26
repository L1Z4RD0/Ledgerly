import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes import gastos, deudas, extras, meses, ahorros

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ledgerly API")

# Si existe la variable FRONTEND_URL en Railway, la usará. 
# Si no existe (en tu PC local), permitirá los puertos por defecto de Vite.
origins = [
    os.getenv("FRONTEND_URL", "http://localhost:5173"),
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # <-- Ahora solo tu frontend podrá hablar con tu backend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(meses.router, prefix="/meses", tags=["meses"])
app.include_router(gastos.router, prefix="/gastos", tags=["gastos"])
app.include_router(deudas.router, prefix="/deudas", tags=["deudas"])
app.include_router(extras.router, prefix="/extras", tags=["extras"])
app.include_router(ahorros.router, prefix="/ahorros", tags=["ahorros"])

@app.get("/")
def root():
    return {"mensaje": "Ledgerly API funcionando"}
Para activar el Backend debes estar en la ruta del backend y encender el entorno virtual posteriormente usar el comando uvicorn

cd "C:\Users\diego\OneDrive - Corporación Santo Tomas\Desktop\Ledgerly\backend"
venv\Scripts\activate
uvicorn main:app --reload

------------------------------------------------------------------------------------------------------------------------------------
Para activar el FrontEnd debes estar en la ruta 

cd "C:\Users\diego\OneDrive - Corporación Santo Tomas\Desktop\Ledgerly\frontend"
y luego hacer un npm run dev para que empiece a correr en local

------------------------------------------------------------------------------------------------------------------------------------
Para hacer el push al GitHub

cd "C:\Users\Diego\Desktop\Ledgerly>"
git add .
git commit -m "fix: saldo entre meses, historial deudas, estadisticas"
git push
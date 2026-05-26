import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ||'http://127.0.0.1:8000',
  headers: {
    'Content-Type': 'application/json'
  }
})

export const mesesService = {
  getAll: () => api.get('/meses/'),
  crear: (anio, mes, sueldoEstimado = 0, saldoInicial = 0) =>
    api.post('/meses/', null, { params: { anio, mes, sueldo_estimado: sueldoEstimado, saldo_inicial: saldoInicial } }),
  getResumen: (mesId) => api.get(`/meses/${mesId}/resumen`),
  actualizarSueldoEstimado: (mesId, sueldoEstimado) => api.put(`/meses/${mesId}/sueldo_estimado?sueldo_estimado=${sueldoEstimado}`),
  cerrar: (mesId, liquido) => api.put(`/meses/${mesId}/cerrar?liquido=${liquido}`)
}

export const gastosService = {
  get: (mesId) => api.get(`/gastos/${mesId}`),
  crear: (mesId, nombre, categoria, monto, fecha) =>
    api.post(`/gastos/${mesId}?nombre=${nombre}&categoria=${categoria}&monto=${monto}&fecha=${fecha}`),
  actualizar: (gastoId, nombre, categoria, monto, fecha) =>
    api.put(`/gastos/${gastoId}?nombre=${nombre}&categoria=${categoria}&monto=${monto}&fecha=${fecha}`),
  eliminar: (gastoId) => api.delete(`/gastos/${gastoId}`),
  porCategoria: (mesId) => api.get(`/gastos/${mesId}/por-categoria`)
}

export const deudasService = {
  getAll: () => api.get('/deudas/'),
  getActivas: () => api.get('/deudas/activas'),
  getPagosMes: (mesId) => api.get(`/deudas/${mesId}/pagos`),
  crear: (nombre, montoTotal, cuota, tipo = 'fijo') =>
    api.post(`/deudas/?nombre=${nombre}&monto_total=${montoTotal}&cuota=${cuota}&tipo=${tipo}`),
  actualizar: (deudaId, nombre, montoTotal, cuota, tipo) =>
    api.put(`/deudas/${deudaId}?nombre=${nombre}&monto_total=${montoTotal}&cuota=${cuota}&tipo=${tipo}`),
  pagar: (deudaId, mesId, monto) =>
    api.post(`/deudas/${deudaId}/pagar?mes_id=${mesId}&monto=${monto}`),
  desactivar: (deudaId) => api.put(`/deudas/${deudaId}/desactivar`),
  eliminar: (deudaId) => api.delete(`/deudas/${deudaId}`)
}

export const extrasService = {
  get: (mesId) => api.get(`/extras/${mesId}`),
  crear: (mesId, descripcion, monto, fecha) =>
    api.post(`/extras/${mesId}?descripcion=${descripcion}&monto=${monto}&fecha=${fecha}`),
  actualizar: (extraId, descripcion, monto, fecha) =>
    api.put(`/extras/${extraId}?descripcion=${descripcion}&monto=${monto}&fecha=${fecha}`),
  eliminar: (extraId) => api.delete(`/extras/${extraId}`)
}

export const ahorrosService = {
  getAll: () => api.get('/ahorros/'),
  getActivos: () => api.get('/ahorros/activos'),
  getAportesMes: (mesId) => api.get(`/ahorros/${mesId}/aportes`),
  crear: (nombre, descripcion, montoMeta, cuota, tipo = 'fijo') =>
    api.post(`/ahorros/?nombre=${nombre}&descripcion=${descripcion}&monto_meta=${montoMeta}&cuota=${cuota}&tipo=${tipo}`),
  actualizar: (ahorroId, nombre, descripcion, montoMeta, cuota, tipo) =>
    api.put(`/ahorros/${ahorroId}?nombre=${nombre}&descripcion=${descripcion}&monto_meta=${montoMeta}&cuota=${cuota}&tipo=${tipo}`),
  aportar: (ahorroId, mesId, monto) =>
    api.post(`/ahorros/${ahorroId}/aportar?mes_id=${mesId}&monto=${monto}`),
  desactivar: (ahorroId) => api.put(`/ahorros/${ahorroId}/desactivar`),
  eliminar: (ahorroId) => api.delete(`/ahorros/${ahorroId}`)
}

export const findicService = {
  getUf: () => axios.get('https://findic.cl/api/uf'),
  getDolar: () => axios.get('https://findic.cl/api/dolar'),
  getEuro: () => axios.get('https://findic.cl/api/euro'),
  getUtm: () => axios.get('https://findic.cl/api/utm'),
  getYen: () => axios.get('https://findic.cl/api/yen'),
  getBitcoin: () => axios.get('https://findic.cl/api/bitcoin')
}
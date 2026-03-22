import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  headers: {
    'Content-Type': 'application/json'
  }
})

export const mesesService = {
  getAll: () => api.get('/meses/'),
  crear: (anio, mes) => api.post(`/meses/?anio=${anio}&mes=${mes}`),
  getResumen: (mesId) => api.get(`/meses/${mesId}/resumen`),
  cerrar: (mesId, liquido, brutoReal = null) => {
    let url = `/meses/${mesId}/cerrar?liquido=${liquido}`
    if (brutoReal) url += `&bruto_real=${brutoReal}`
    return api.put(url)
  }
}

export const turnosService = {
  get: (mesId) => api.get(`/turnos/${mesId}`),
  crear: (mesId, numeroSemana, turnos, valorTurno = 16000) =>
    api.post(`/turnos/${mesId}?numero_semana=${numeroSemana}&turnos=${turnos}&valor_turno=${valorTurno}`),
  actualizar: (semanaId, turnos, valorTurno = 16000) =>
    api.put(`/turnos/${semanaId}?turnos=${turnos}&valor_turno=${valorTurno}`),
  eliminar: (semanaId) => api.delete(`/turnos/${semanaId}`)
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
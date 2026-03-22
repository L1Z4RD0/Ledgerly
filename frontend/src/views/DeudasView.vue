<template>
  <div class="view">
    <div class="topbar">
      <div>
        <div class="topbar-title">Deudas</div>
        <div class="topbar-sub">{{ deudas.length }} deudas registradas</div>
      </div>
      <div class="topbar-actions">
        <select v-model="mesSeleccionado" @change="cargarPagosMes" class="select-mes">
          <option v-for="m in meses" :key="m.id" :value="m.id">
            {{ nombreMes(m.mes) }} {{ m.anio }}
          </option>
        </select>
        <button @click="mostrarModal = true" class="btn-primary">+ Nueva deuda</button>
      </div>
    </div>

    <div class="page-content">
      <div class="metrics-row">
        <div class="metric-card">
          <div class="metric-label">Deudas activas</div>
          <div class="metric-val">{{ deudasActivas.length }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Pagado este mes</div>
          <div class="metric-val red">{{ formatCLP(totalPagadoMes) }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Total restante</div>
          <div class="metric-val red">{{ formatCLP(totalRestante) }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Total pagado histórico</div>
          <div class="metric-val green">{{ formatCLP(totalPagadoHistorico) }}</div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Deudas activas</div>
        <div v-if="deudasActivas.length === 0" class="empty-state">Sin deudas activas</div>
        <div v-for="d in deudasActivas" :key="d.id" class="debt-item">
          <div class="debt-header">
            <div>
              <div class="debt-nombre">{{ d.nombre }}</div>
              <div class="debt-cuota">
                Cuota sugerida: {{ d.tipo === 'fijo' ? formatCLP(d.cuota) + '/mes' : d.cuota + '% del sueldo' }}
              </div>
            </div>
            <div class="debt-actions">
              <button @click="abrirPago(d)" class="btn-pagar">Registrar pago</button>
              <button @click="desactivar(d.id)" class="btn-delete">×</button>
            </div>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: pctPagado(d) + '%' }"></div>
          </div>
          <div class="debt-footer">
            <span>{{ formatCLP(d.monto_pagado) }} pagado</span>
            <span>{{ formatCLP(d.monto_total - d.monto_pagado) }} restante</span>
          </div>
        </div>
      </div>

      <div class="card" v-if="pagosMes.length > 0">
        <div class="card-title">Pagos registrados este mes</div>
        <div v-for="p in pagosMes" :key="p.id" class="pago-row">
          <div class="pago-info">
            <div class="pago-nombre">{{ p.nombre_deuda }}</div>
            <div class="pago-fecha">{{ p.fecha }}</div>
          </div>
          <span class="pago-monto">−{{ formatCLP(p.monto) }}</span>
        </div>
        <div class="pago-total">
          <span>Total pagado este mes</span>
          <span class="red">−{{ formatCLP(totalPagadoMes) }}</span>
        </div>
      </div>

      <div class="card" v-if="deudasInactivas.length > 0">
        <div class="card-title">Deudas pagadas</div>
        <div v-for="d in deudasInactivas" :key="d.id" class="debt-item">
          <div class="debt-header">
            <div>
              <div class="debt-nombre" style="color:var(--text-muted)">{{ d.nombre }}</div>
              <div class="debt-cuota">{{ formatCLP(d.monto_total) }} — pagado completo</div>
            </div>
            <span class="badge-ok">Pagada</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" style="width:100%;background:#1D9E75"></div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="mostrarModal" class="modal-overlay" @click.self="mostrarModal = false">
      <div class="modal">
        <div class="modal-title">Nueva deuda</div>
        <div class="form-group">
          <label>Nombre</label>
          <input v-model="nuevaNombre" type="text" class="input" placeholder="Ej: Préstamo banco" />
        </div>
        <div class="form-group">
          <label>Monto total</label>
          <input v-model="nuevoMontoTotal" type="number" class="input" placeholder="Ej: 600000" />
        </div>
        <div class="form-group">
          <label>Tipo de cuota</label>
          <select v-model="nuevoTipo" class="input">
            <option value="fijo">Monto fijo mensual</option>
            <option value="porcentaje">Porcentaje del sueldo</option>
          </select>
        </div>
        <div class="form-group">
          <label>{{ nuevoTipo === 'fijo' ? 'Cuota sugerida (CLP)' : 'Porcentaje (%)' }}</label>
          <input v-model="nuevaCuota" type="number" class="input" :placeholder="nuevoTipo === 'fijo' ? 'Ej: 60000' : 'Ej: 5'" />
        </div>
        <div class="modal-actions">
          <button @click="mostrarModal = false" class="btn-secondary">Cancelar</button>
          <button @click="crearDeuda" class="btn-primary">Crear</button>
        </div>
      </div>
    </div>

    <div v-if="mostrarModalPago" class="modal-overlay" @click.self="mostrarModalPago = false">
      <div class="modal">
        <div class="modal-title">Registrar pago — {{ deudaSeleccionada?.nombre }}</div>
        <div class="form-group">
          <label>Monto a pagar (CLP)</label>
          <input v-model="montoPago" type="number" class="input" :placeholder="'Sugerido: ' + deudaSeleccionada?.cuota" />
        </div>
        <div class="aviso" v-if="!mesSeleccionado">Selecciona un mes primero</div>
        <div class="modal-actions">
          <button @click="mostrarModalPago = false" class="btn-secondary">Cancelar</button>
          <button @click="registrarPago" class="btn-primary" :disabled="!mesSeleccionado">Registrar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { mesesService, deudasService } from '../services/api'

const meses = ref([])
const mesSeleccionado = ref(null)
const deudas = ref([])
const pagosMes = ref([])
const mostrarModal = ref(false)
const mostrarModalPago = ref(false)
const deudaSeleccionada = ref(null)
const montoPago = ref('')
const nuevaNombre = ref('')
const nuevoMontoTotal = ref('')
const nuevoTipo = ref('fijo')
const nuevaCuota = ref('')

const nombresMeses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
const nombreMes = (n) => nombresMeses[n - 1]
const formatCLP = (n) => '$' + Math.round(n || 0).toLocaleString('es-CL')
const pctPagado = (d) => d.monto_total > 0 ? Math.min(100, Math.round((d.monto_pagado / d.monto_total) * 100)) : 0

const deudasActivas = computed(() => deudas.value.filter(d => d.activa))
const deudasInactivas = computed(() => deudas.value.filter(d => !d.activa))
const totalPagadoMes = computed(() => pagosMes.value.reduce((acc, p) => acc + p.monto, 0))
const totalRestante = computed(() => deudasActivas.value.reduce((acc, d) => acc + (d.monto_total - d.monto_pagado), 0))
const totalPagadoHistorico = computed(() => deudas.value.reduce((acc, d) => acc + d.monto_pagado, 0))

const cargarMeses = async () => {
  const res = await mesesService.getAll()
  meses.value = res.data
  if (meses.value.length > 0) {
    mesSeleccionado.value = meses.value[meses.value.length - 1].id
    await cargarPagosMes()
  }
}

const cargarDeudas = async () => {
  const res = await deudasService.getAll()
  deudas.value = res.data
}

const cargarPagosMes = async () => {
  if (!mesSeleccionado.value) return
  const res = await deudasService.getPagosMes(mesSeleccionado.value)
  pagosMes.value = res.data
}

const crearDeuda = async () => {
  if (!nuevaNombre.value || !nuevoMontoTotal.value || !nuevaCuota.value) return
  await deudasService.crear(nuevaNombre.value, nuevoMontoTotal.value, nuevaCuota.value, nuevoTipo.value)
  nuevaNombre.value = ''
  nuevoMontoTotal.value = ''
  nuevaCuota.value = ''
  mostrarModal.value = false
  await cargarDeudas()
}

const abrirPago = (d) => {
  deudaSeleccionada.value = d
  montoPago.value = d.cuota
  mostrarModalPago.value = true
}

const registrarPago = async () => {
  if (!montoPago.value || !mesSeleccionado.value) return
  await deudasService.pagar(deudaSeleccionada.value.id, mesSeleccionado.value, montoPago.value)
  mostrarModalPago.value = false
  montoPago.value = ''
  await cargarDeudas()
  await cargarPagosMes()
}

const desactivar = async (id) => {
  await deudasService.desactivar(id)
  await cargarDeudas()
}

onMounted(async () => {
  await cargarDeudas()
  await cargarMeses()
})
</script>

<style scoped>
.view { min-height: 100vh; background: var(--bg); color: var(--text-primary); }
.topbar { padding: 16px 24px; background: var(--bg-card); border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; }
.topbar-title { font-size: 16px; font-weight: 600; color: var(--text-primary); }
.topbar-sub { font-size: 12px; color: var(--text-secondary); margin-top: 2px; }
.topbar-actions { display: flex; gap: 10px; align-items: center; }
.select-mes { padding: 6px 10px; border: 1px solid var(--border); border-radius: 8px; font-size: 13px; background: var(--bg-card); color: var(--text-primary); }
.page-content { padding: 20px 24px; display: flex; flex-direction: column; gap: 16px; }
.metrics-row { display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 12px; }
.metric-card { background: var(--bg-metric); border-radius: 10px; padding: 14px; }
.metric-label { font-size: 11px; color: var(--text-secondary); margin-bottom: 6px; }
.metric-val { font-size: 20px; font-weight: 600; color: var(--text-primary); }
.metric-val.red { color: #993C1D; }
.metric-val.green { color: #0F6E56; }
.card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 16px; }
.card-title { font-size: 11px; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 14px; }
.debt-item { padding: 12px 0; border-bottom: 1px solid var(--border-light); }
.debt-item:last-child { border-bottom: none; }
.debt-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; }
.debt-nombre { font-size: 14px; font-weight: 600; color: var(--text-primary); }
.debt-cuota { font-size: 12px; color: var(--text-secondary); margin-top: 2px; }
.debt-actions { display: flex; gap: 8px; align-items: center; }
.btn-pagar { padding: 6px 12px; background: #E6F1FB; color: #185FA5; border: none; border-radius: 6px; font-size: 12px; cursor: pointer; font-weight: 500; }
.btn-pagar:hover { background: #B5D4F4; }
.btn-delete { background: none; border: none; color: var(--text-muted); font-size: 20px; cursor: pointer; }
.btn-delete:hover { color: #993C1D; }
.progress-bar { background: var(--bg-metric); border-radius: 4px; height: 6px; overflow: hidden; margin-bottom: 6px; }
.progress-fill { height: 100%; border-radius: 4px; background: #185FA5; transition: width 0.3s; }
.debt-footer { display: flex; justify-content: space-between; font-size: 11px; color: var(--text-muted); }
.pago-row { display: flex; align-items: center; justify-content: space-between; padding: 9px 0; border-bottom: 1px solid var(--border-light); }
.pago-row:last-of-type { border-bottom: none; }
.pago-info .pago-nombre { font-size: 13px; font-weight: 500; color: var(--text-primary); }
.pago-info .pago-fecha { font-size: 11px; color: var(--text-muted); margin-top: 2px; }
.pago-monto { font-size: 14px; font-weight: 600; color: #993C1D; }
.pago-total { display: flex; justify-content: space-between; padding-top: 12px; margin-top: 8px; border-top: 1px solid var(--border); font-size: 14px; font-weight: 600; }
.badge-ok { background: #EAF3DE; color: #3B6D11; font-size: 11px; padding: 4px 10px; border-radius: 6px; font-weight: 500; }
.empty-state { font-size: 13px; color: var(--text-muted); text-align: center; padding: 20px 0; }
.btn-primary { padding: 8px 16px; background: #185FA5; color: #fff; border: none; border-radius: 8px; font-size: 13px; cursor: pointer; }
.btn-primary:hover { background: #0C447C; }
.btn-primary:disabled { background: #aaa; cursor: not-allowed; }
.btn-secondary { padding: 8px 16px; background: var(--bg-card); color: var(--text-primary); border: 1px solid var(--border); border-radius: 8px; font-size: 13px; cursor: pointer; }
.form-group { margin-bottom: 12px; }
.form-group label { font-size: 12px; color: var(--text-secondary); display: block; margin-bottom: 4px; }
.input { width: 100%; padding: 8px 12px; border: 1px solid var(--border); border-radius: 8px; font-size: 13px; background: var(--bg-card); color: var(--text-primary); }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 200; }
.modal { background: var(--bg-card); border-radius: 14px; padding: 24px; width: 340px; }
.modal-title { font-size: 15px; font-weight: 600; margin-bottom: 16px; color: var(--text-primary); }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 16px; }
.aviso { font-size: 12px; color: #854F0B; background: #FAEEDA; padding: 8px 12px; border-radius: 6px; margin-top: 8px; }
.red { color: #993C1D; }

@media (max-width: 768px) {
  .metrics-row { grid-template-columns: 1fr 1fr; }
}
</style>
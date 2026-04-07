<template>
  <div class="view">
    <div class="topbar">
      <div>
        <div class="topbar-title">Ingresos extra</div>
        <div class="topbar-sub">{{ mesLabel }}</div>
      </div>
      <select v-model="mesSeleccionado" @change="cargarExtras" class="select-mes">
        <option v-for="m in meses" :key="m.id" :value="m.id">
          {{ nombreMes(m.mes) }} {{ m.anio }}
        </option>
      </select>
    </div>

    <div class="page-content">
      <div class="metrics-row">
        <div class="metric-card">
          <div class="metric-label">Total extras este mes</div>
          <div class="metric-val green">{{ formatCLP(totalExtras) }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Registros</div>
          <div class="metric-val">{{ extras.length }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Promedio por ingreso</div>
          <div class="metric-val">{{ formatCLP(promedio) }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Mayor ingreso</div>
          <div class="metric-val blue">{{ formatCLP(mayor) }}</div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Agregar ingreso extra</div>
        <div class="form-row">
          <div class="form-group">
            <label>Descripción</label>
            <input v-model="nuevaDesc" type="text" class="input" placeholder="Ej: Bono, subsidio, regalo..." />
          </div>
          <div class="form-group">
            <label>Monto (CLP)</label>
            <input v-model="nuevoMonto" type="number" class="input" placeholder="Ej: 30000" min="0" @keypress="$event.key.toLowerCase() === 'e' && $event.preventDefault()" />
          </div>
          <div class="form-group">
            <label>Fecha</label>
            <input v-model="nuevaFecha" type="date" class="input" />
          </div>
          <button @click="agregarExtra" class="btn-primary" style="align-self:flex-end">Agregar</button>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Registros del mes</div>
        <div v-if="extras.length === 0" class="empty-state">Sin ingresos extra registrados aún</div>
        <div v-for="e in extrasOrdenados" :key="e.id" class="extra-row">
          <div class="extra-icon">+</div>
          <div class="extra-info">
            <div class="extra-nombre">{{ e.descripcion }}</div>
            <div class="extra-fecha">{{ e.fecha }}</div>
          </div>
          <span class="extra-monto">+{{ formatCLP(e.monto) }}</span>
          <button @click="eliminarExtra(e.id)" class="btn-delete">×</button>
        </div>
        <div v-if="extras.length > 0" class="extra-total">
          <span>Total ingresos extra</span>
          <span class="green">+{{ formatCLP(totalExtras) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { mesesService, extrasService } from '../services/api'

const meses = ref([])
const mesSeleccionado = ref(null)
const extras = ref([])
const nuevaDesc = ref('')
const nuevoMonto = ref('')
const nuevaFecha = ref(new Date().toISOString().split('T')[0])

const nombresMeses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
const nombreMes = (n) => nombresMeses[n - 1]
const formatCLP = (n) => '$' + Math.round(n || 0).toLocaleString('es-CL')

const mesLabel = computed(() => {
  if (!mesSeleccionado.value || !meses.value.length) return ''
  const m = meses.value.find(x => x.id === mesSeleccionado.value)
  return m ? `${nombreMes(m.mes)} ${m.anio}` : ''
})

const totalExtras = computed(() => extras.value.reduce((acc, e) => acc + e.monto, 0))
const promedio = computed(() => extras.value.length > 0 ? totalExtras.value / extras.value.length : 0)
const mayor = computed(() => extras.value.length > 0 ? Math.max(...extras.value.map(e => e.monto)) : 0)
const extrasOrdenados = computed(() => [...extras.value].sort((a, b) => new Date(b.fecha) - new Date(a.fecha)))

const cargarMeses = async () => {
  const res = await mesesService.getAll()
  meses.value = res.data
  if (meses.value.length > 0) {
    mesSeleccionado.value = meses.value[meses.value.length - 1].id
    await cargarExtras()
  }
}

const cargarExtras = async () => {
  if (!mesSeleccionado.value) return
  const res = await extrasService.get(mesSeleccionado.value)
  extras.value = res.data
}

const agregarExtra = async () => {
  if (!nuevaDesc.value || !nuevoMonto.value) return
  await extrasService.crear(mesSeleccionado.value, nuevaDesc.value, nuevoMonto.value, nuevaFecha.value)
  nuevaDesc.value = ''
  nuevoMonto.value = ''
  await cargarExtras()
}

const eliminarExtra = async (id) => {
  await extrasService.eliminar(id)
  await cargarExtras()
}

onMounted(cargarMeses)
</script>

<style scoped>
.view { min-height: 100vh; background: #f5f5f3; }
.topbar { padding: 16px 24px; background: #fff; border-bottom: 1px solid #e5e5e3; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; }
.topbar-title { font-size: 16px; font-weight: 600; }
.topbar-sub { font-size: 12px; color: #888; margin-top: 2px; }
.select-mes { padding: 6px 10px; border: 1px solid #e5e5e3; border-radius: 8px; font-size: 13px; background: #fff; }
.page-content { padding: 20px 24px; display: flex; flex-direction: column; gap: 16px; }
.metrics-row { display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 12px; }
.metric-card { background: #efefed; border-radius: 10px; padding: 14px; }
.metric-label { font-size: 11px; color: #888; margin-bottom: 6px; }
.metric-val { font-size: 20px; font-weight: 600; }
.metric-val.green { color: #0F6E56; }
.metric-val.blue { color: #185FA5; }
.card { background: #fff; border: 1px solid #e5e5e3; border-radius: 12px; padding: 16px; }
.card-title { font-size: 11px; font-weight: 600; color: #888; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 14px; }
.form-row { display: flex; gap: 12px; flex-wrap: wrap; }
.form-group { flex: 1; min-width: 130px; }
.form-group label { font-size: 12px; color: #888; display: block; margin-bottom: 4px; }
.input { width: 100%; padding: 8px 12px; border: 1px solid #e5e5e3; border-radius: 8px; font-size: 13px; }
.btn-primary { padding: 8px 16px; background: #185FA5; color: #fff; border: none; border-radius: 8px; font-size: 13px; cursor: pointer; white-space: nowrap; }
.btn-primary:hover { background: #0C447C; }
.extra-row { display: flex; align-items: center; gap: 10px; padding: 10px 0; border-bottom: 1px solid #f0f0ee; }
.extra-row:last-of-type { border-bottom: none; }
.extra-icon { width: 28px; height: 28px; border-radius: 50%; background: #EAF3DE; color: #3B6D11; display: flex; align-items: center; justify-content: center; font-size: 16px; font-weight: 600; flex-shrink: 0; }
.extra-info { flex: 1; }
.extra-nombre { font-size: 13px; font-weight: 500; }
.extra-fecha { font-size: 11px; color: #aaa; margin-top: 2px; }
.extra-monto { font-size: 14px; font-weight: 600; color: #0F6E56; }
.btn-delete { background: none; border: none; color: #ccc; font-size: 18px; cursor: pointer; padding: 0 4px; }
.btn-delete:hover { color: #993C1D; }
.extra-total { display: flex; justify-content: space-between; padding-top: 12px; margin-top: 8px; border-top: 1px solid #e5e5e3; font-size: 14px; font-weight: 600; }
.empty-state { font-size: 13px; color: #aaa; text-align: center; padding: 20px 0; }
.green { color: #0F6E56; }

@media (max-width: 768px) {
  .metrics-row { grid-template-columns: 1fr 1fr; }
}
</style>
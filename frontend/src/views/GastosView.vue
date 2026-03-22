<template>
  <div class="view">
    <div class="topbar">
      <div>
        <div class="topbar-title">Gastos</div>
        <div class="topbar-sub">{{ mesLabel }}</div>
      </div>
      <select v-model="mesSeleccionado" @change="cargarGastos" class="select-mes">
        <option v-for="m in meses" :key="m.id" :value="m.id">
          {{ nombreMes(m.mes) }} {{ m.anio }}
        </option>
      </select>
    </div>

    <div class="page-content">
      <div class="metrics-row">
        <div class="metric-card">
          <div class="metric-label">Neto disponible</div>
          <div class="metric-val">{{ formatCLP(netoDisponible) }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Total gastado</div>
          <div class="metric-val red">{{ formatCLP(totalGastos) }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Registros</div>
          <div class="metric-val">{{ gastos.length }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Saldo restante</div>
          <div class="metric-val" :class="saldoRestante >= 0 ? 'green' : 'red'">
            {{ formatCLP(saldoRestante) }}
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Agregar gasto</div>
        <div class="form-row">
          <div class="form-group">
            <label>Nombre</label>
            <input v-model="nuevoNombre" type="text" class="input" placeholder="Ej: Supermercado Lider" />
          </div>
          <div class="form-group">
            <label>Categoría</label>
            <select v-model="nuevaCategoria" class="input">
              <option v-for="cat in categorias" :key="cat" :value="cat">{{ cat }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>Monto (CLP)</label>
            <input v-model="nuevoMonto" type="number" class="input" placeholder="Ej: 15000" />
          </div>
          <div class="form-group">
            <label>Fecha</label>
            <input v-model="nuevaFecha" type="date" class="input" />
          </div>
          <button @click="agregarGasto" class="btn-primary" style="align-self:flex-end">Agregar</button>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Registro del mes</div>
        <div v-if="gastos.length === 0" class="empty-state">Sin gastos registrados aún</div>
        <div v-for="g in gastosOrdenados" :key="g.id" class="gasto-row">
          <div class="gasto-dot" :style="{ background: colorCategoria(g.categoria) }"></div>
          <div class="gasto-info">
            <div class="gasto-nombre">{{ g.nombre }}</div>
            <div class="gasto-cat">{{ g.categoria }} · {{ g.fecha }}</div>
          </div>
          <span class="gasto-monto">−{{ formatCLP(g.monto) }}</span>
          <button @click="eliminarGasto(g.id)" class="btn-delete">×</button>
        </div>
        <div v-if="gastos.length > 0" class="gasto-total">
          <span>Total gastado</span>
          <span class="red">−{{ formatCLP(totalGastos) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { mesesService, gastosService } from '../services/api'

const meses = ref([])
const mesSeleccionado = ref(null)
const gastos = ref([])
const resumen = ref(null)
const nuevoNombre = ref('')
const nuevaCategoria = ref('Alimentación')
const nuevoMonto = ref('')
const nuevaFecha = ref(new Date().toISOString().split('T')[0])

const categorias = ['Alimentación', 'Transporte', 'Servicios', 'Salud', 'Educación', 'Libros', 'Entretenimiento', 'Ropa', 'Tecnología', 'Otros']

const coloresCat = {
  'Alimentación': '#185FA5',
  'Transporte': '#D85A30',
  'Servicios': '#854F0B',
  'Salud': '#D4537E',
  'Educación': '#534AB7',
  'Libros': '#1D9E75',
  'Entretenimiento': '#7F77DD',
  'Ropa': '#D4537E',
  'Tecnología': '#378ADD',
  'Otros': '#888780'
}

const nombresMeses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
const nombreMes = (n) => nombresMeses[n - 1]
const colorCategoria = (cat) => coloresCat[cat] || '#888780'
const formatCLP = (n) => '$' + Math.round(n || 0).toLocaleString('es-CL')

const mesLabel = computed(() => {
  if (!mesSeleccionado.value || !meses.value.length) return ''
  const m = meses.value.find(x => x.id === mesSeleccionado.value)
  return m ? `${nombreMes(m.mes)} ${m.anio}` : ''
})

const totalGastos = computed(() => gastos.value.reduce((acc, g) => acc + g.monto, 0))
const netoDisponible = computed(() => resumen.value ? resumen.value.neto_final : 0)
const saldoRestante = computed(() => netoDisponible.value - totalGastos.value)
const gastosOrdenados = computed(() => [...gastos.value].sort((a, b) => new Date(b.fecha) - new Date(a.fecha)))

const cargarMeses = async () => {
  const res = await mesesService.getAll()
  meses.value = res.data
  if (meses.value.length > 0) {
    mesSeleccionado.value = meses.value[meses.value.length - 1].id
    await cargarGastos()
  }
}

const cargarGastos = async () => {
  if (!mesSeleccionado.value) return
  const res = await gastosService.get(mesSeleccionado.value)
  gastos.value = res.data
  try {
    const r = await mesesService.getResumen(mesSeleccionado.value)
    resumen.value = r.data
  } catch {
    resumen.value = null
  }
}

const agregarGasto = async () => {
  if (!nuevoNombre.value || !nuevoMonto.value) return
  await gastosService.crear(mesSeleccionado.value, nuevoNombre.value, nuevaCategoria.value, nuevoMonto.value, nuevaFecha.value)
  nuevoNombre.value = ''
  nuevoMonto.value = ''
  await cargarGastos()
}

const eliminarGasto = async (id) => {
  await gastosService.eliminar(id)
  await cargarGastos()
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
.metric-val.red { color: #993C1D; }
.metric-val.green { color: #0F6E56; }
.card { background: #fff; border: 1px solid #e5e5e3; border-radius: 12px; padding: 16px; }
.card-title { font-size: 11px; font-weight: 600; color: #888; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 14px; }
.form-row { display: flex; gap: 12px; flex-wrap: wrap; }
.form-group { flex: 1; min-width: 130px; }
.form-group label { font-size: 12px; color: #888; display: block; margin-bottom: 4px; }
.input { width: 100%; padding: 8px 12px; border: 1px solid #e5e5e3; border-radius: 8px; font-size: 13px; }
.btn-primary { padding: 8px 16px; background: #185FA5; color: #fff; border: none; border-radius: 8px; font-size: 13px; cursor: pointer; white-space: nowrap; }
.btn-primary:hover { background: #0C447C; }
.gasto-row { display: flex; align-items: center; gap: 10px; padding: 10px 0; border-bottom: 1px solid #f0f0ee; }
.gasto-row:last-of-type { border-bottom: none; }
.gasto-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.gasto-info { flex: 1; }
.gasto-nombre { font-size: 13px; font-weight: 500; }
.gasto-cat { font-size: 11px; color: #aaa; margin-top: 2px; }
.gasto-monto { font-size: 14px; font-weight: 600; color: #993C1D; }
.btn-delete { background: none; border: none; color: #ccc; font-size: 18px; cursor: pointer; padding: 0 4px; }
.btn-delete:hover { color: #993C1D; }
.gasto-total { display: flex; justify-content: space-between; padding-top: 12px; margin-top: 8px; border-top: 1px solid #e5e5e3; font-size: 14px; font-weight: 600; }
.empty-state { font-size: 13px; color: #aaa; text-align: center; padding: 20px 0; }
.red { color: #993C1D; }

@media (max-width: 768px) {
  .metrics-row { grid-template-columns: 1fr 1fr; }
}
</style>
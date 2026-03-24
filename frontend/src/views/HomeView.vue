<template>
  <div class="view">
    <div class="topbar">
      <div>
        <div class="topbar-title">Inicio — resumen del mes</div>
        <div class="topbar-sub">{{ mesLabel }} · {{ resumen?.mes_cerrado ? 'Cerrado' : 'En curso' }}</div>
      </div>
      <div class="topbar-actions">
        <select v-model="mesSeleccionado" @change="cargarResumen" class="select-mes">
          <option v-for="m in meses" :key="m.id" :value="m.id">
            {{ nombreMes(m.mes) }} {{ m.anio }}
          </option>
        </select>
        <button @click="mostrarModalNuevoMes = true" class="btn-primary">+ Nuevo mes</button>
      </div>
    </div>

    <div class="page-content" v-if="resumen">
      <div class="metrics-row">
        <div class="metric-card">
          <div class="metric-label">Bruto estimado</div>
          <div class="metric-val">{{ formatCLP(resumen.bruto) }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">AFP + Fonasa (est.)</div>
          <div class="metric-val red">−{{ formatCLP(resumen.descuento_afp + resumen.descuento_fonasa) }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Neto estimado</div>
          <div class="metric-val blue">{{ formatCLP(resumen.neto_estimado) }}</div>
        </div>
        
        <div class="metric-card" :class="{ 'is-critical': !resumen.mes_cerrado && resumen.saldo_disponible < 50000 }">
          <div class="metric-label">{{ resumen.mes_cerrado ? 'Saldo libre final' : 'Disponible ahora' }}</div>
          <div class="metric-val green" v-if="resumen.mes_cerrado">{{ formatCLP(resumen.saldo_libre) }}</div>
          <div class="metric-val green" v-else>
            {{ formatCLP(resumen.saldo_disponible) }}
            <span v-if="resumen.saldo_disponible < 50000" class="mini-alert">⚠️ Bajo</span>
          </div>
        </div>
      </div>

      <div class="two-col">
        <div class="card">
          <div class="card-title">Desglose mensual</div>

          <div class="section-label">Estimación</div>
          <div class="breakdown-row">
            <span class="lbl">Bruto estimado</span>
            <span>{{ formatCLP(resumen.bruto) }}</span>
          </div>
          <div class="breakdown-row">
            <span class="lbl">AFP (10,46%)</span>
            <span class="neg">−{{ formatCLP(resumen.descuento_afp) }}</span>
          </div>
          <div class="breakdown-row">
            <span class="lbl">Fonasa (7%)</span>
            <span class="neg">−{{ formatCLP(resumen.descuento_fonasa) }}</span>
          </div>
          <div class="breakdown-row total">
            <span>Neto estimado</span>
            <span class="blue">{{ formatCLP(resumen.neto_estimado) }}</span>
          </div>

          <template v-if="resumen.mes_cerrado">
            <div class="section-label" style="margin-top:16px">Real</div>
            <div class="breakdown-row">
              <span class="lbl">Saldo mes anterior</span>
              <span class="pos">{{ formatCLP(resumen.saldo_anterior) }}</span>
            </div>
            <div class="breakdown-row">
              <span class="lbl">Líquido recibido</span>
              <span class="pos">+{{ formatCLP(resumen.sueldo_real) }}</span>
            </div>
            <div class="breakdown-row" v-if="resumen.total_extras > 0">
              <span class="lbl">Ingresos extra</span>
              <span class="pos">+{{ formatCLP(resumen.total_extras) }}</span>
            </div>
            <div class="breakdown-row" v-if="resumen.total_pagos_deuda > 0">
              <span class="lbl">Pagos de deudas</span>
              <span class="neg">−{{ formatCLP(resumen.total_pagos_deuda) }}</span>
            </div>
            <div class="breakdown-row" v-if="resumen.total_gastos > 0">
              <span class="lbl">Gastos registrados</span>
              <span class="neg">−{{ formatCLP(resumen.total_gastos) }}</span>
            </div>
            <div class="breakdown-row total">
              <span>Saldo libre final</span>
              <span class="green">{{ formatCLP(resumen.saldo_libre) }}</span>
            </div>
            <div class="breakdown-row" v-if="resumen.diferencia_bruto !== null">
              <span class="lbl">Diferencia estimado/real</span>
              <span :class="resumen.diferencia_bruto >= 0 ? 'pos' : 'neg'">
                {{ resumen.diferencia_bruto >= 0 ? '+' : '' }}{{ formatCLP(resumen.diferencia_bruto) }}
              </span>
            </div>
          </template>

          <template v-else>
            <div class="section-label" style="margin-top:16px">Disponible ahora</div>
            <div class="breakdown-row">
              <span class="lbl">Saldo mes anterior</span>
              <span class="pos">{{ formatCLP(resumen.saldo_anterior) }}</span>
            </div>
            <div class="breakdown-row" v-if="resumen.total_extras > 0">
              <span class="lbl">Ingresos extra</span>
              <span class="pos">+{{ formatCLP(resumen.total_extras) }}</span>
            </div>
            <div class="breakdown-row" v-if="resumen.total_gastos > 0">
              <span class="lbl">Gastos registrados</span>
              <span class="neg">−{{ formatCLP(resumen.total_gastos) }}</span>
            </div>
            <div class="breakdown-row" v-if="resumen.total_pagos_deuda > 0">
              <span class="lbl">Pagos de deudas</span>
              <span class="neg">−{{ formatCLP(resumen.total_pagos_deuda) }}</span>
            </div>
            <div class="breakdown-row total">
              <span>Disponible ahora</span>
              <span :class="resumen.saldo_disponible >= 0 ? 'green' : 'neg'">
                {{ formatCLP(resumen.saldo_disponible) }}
              </span>
            </div>
            <div class="aviso-mes">
              Cierra el mes al recibir tu líquido para calcular el saldo final
            </div>
          </template>
        </div>

        <div class="card">
          <div class="card-title">Análisis de Gastos</div>
          <div v-if="Object.keys(gastosCat).length === 0" class="empty-state">
            Sin gastos registrados
          </div>
          <template v-else>
            <div style="margin-bottom: 16px;">
              <div class="donut-chart-wrapper">
                <apexchart type="donut" height="240" :options="donutEsencialOptions" :series="[gastosEsencial, gastosDiscrecional]"></apexchart>
              </div>
              <div class="donut-legend">
                <div class="legend-item">
                  <span class="legend-dot" style="background: #0F6E56;"></span>
                  <span>Esencial: {{ formatCLP(gastosEsencial) }}</span>
                </div>
                <div class="legend-item">
                  <span class="legend-dot" style="background: #185FA5;"></span>
                  <span>Discrecional: {{ formatCLP(gastosDiscrecional) }}</span>
                </div>
              </div>
            </div>
            <div style="border-top: 1px solid var(--border); padding-top: 12px;">
              <div class="topbar-title" style="font-size: 12px; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.5px;">Top 3 categorías</div>
              <div v-for="item in categoriasPrincipales" :key="item.cat" class="top-cat-row">
                <span class="cat-name">{{ item.cat }}</span>
                <span class="cat-monto">{{ formatCLP(item.monto) }}</span>
              </div>
            </div>
          </template>
        </div>
      </div>

      <div v-if="!resumen.mes_cerrado" class="card">
        <div class="card-title">Cerrar mes</div>
        <p class="cerrar-desc">Ingresa los valores de tu liquidación de sueldo al recibirla</p>
        <div class="form-row">
          <div class="form-group">
            <label>Sueldo bruto (opcional, para referencia)</label>
            <input v-model="sueldoBrutoReal" type="number" placeholder="Ej: 208000" class="input" />
          </div>
          <div class="form-group">
            <label>Líquido a pago (requerido)</label>
            <input v-model="sueldoReal" type="number" placeholder="Ej: 140268" class="input" />
          </div>
          <button @click="cerrarMes" class="btn-primary" style="align-self:flex-end">Cerrar mes</button>
        </div>
      </div>
    </div>

    <div class="page-content" v-else>
      <div class="empty-state-big">
        <p>No hay datos para este mes todavía.</p>
        <p>Agrega turnos en la sección Turnos para comenzar.</p>
      </div>
    </div>

    <div v-if="mostrarModalNuevoMes" class="modal-overlay" @click.self="mostrarModalNuevoMes = false">
      <div class="modal">
        <div class="modal-title">Crear nuevo mes</div>
        <div class="form-group">
          <label>Año</label>
          <input v-model="nuevoAnio" type="number" class="input" placeholder="2026" />
        </div>
        <div class="form-group">
          <label>Mes</label>
          <select v-model="nuevoMes" class="input">
            <option v-for="(nombre, idx) in nombresMeses" :key="idx" :value="idx + 1">{{ nombre }}</option>
          </select>
        </div>
        <div class="modal-actions">
          <button @click="mostrarModalNuevoMes = false" class="btn-secondary">Cancelar</button>
          <button @click="crearMes" class="btn-primary">Crear</button>
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
const resumen = ref(null)
const gastosCat = ref({})
const gastosEsencial = computed(() => {
  const palabrasClave = ['almuerzo', 'comida', 'compra', 'super', 'mercado', 'verdura', 'carne', 'pan', 'leche', 'arriendo', 'luz', 'agua', 'internet', 'telefono', 'transporte', 'bencina', 'metro', 'pasaje', 'medico', 'farmacia', 'medicina']
  let esencial = 0
  for (const [cat, monto] of Object.entries(gastosCat.value)) {
    const lower = cat.toLowerCase()
    if (palabrasClave.some(p => lower.includes(p))) {
      esencial += monto
    }
  }
  return esencial
})

const gastosDiscrecional = computed(() => {
  const total = Object.values(gastosCat.value).reduce((a, b) => a + b, 0)
  return total - gastosEsencial.value
})

const categoriasPrincipales = computed(() => {
  const sorted = Object.entries(gastosCat.value)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3)
    .map(([cat, monto]) => ({ cat, monto }))
  return sorted
})
const sueldoBrutoReal = ref('')
const mostrarModalNuevoMes = ref(false)
const nuevoAnio = ref(new Date().getFullYear())
const nuevoMes = ref(new Date().getMonth() + 1)

const nombresMeses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']

const mesLabel = computed(() => {
  if (!mesSeleccionado.value || !meses.value.length) return ''
  const m = meses.value.find(x => x.id === mesSeleccionado.value)
  if (!m) return ''
  return `${nombresMeses[m.mes - 1]} ${m.anio}`
})

const formatCLP = (n) => {
  if (n === null || n === undefined) return '$0'
  return '$' + Math.round(n).toLocaleString('es-CL')
}

const nombreMes = (n) => nombresMeses[n - 1]

const pctGasto = (monto) => {
  const values = Object.values(gastosCat.value)
  if (values.length === 0) return 0
  const max = Math.max(...values)
  return max > 0 ? Math.round((monto / max) * 100) : 0
}

const donutEsencialOptions = {
  labels: ['Esencial', 'Discrecional'],
  chart: { fontFamily: 'inherit', toolbar: { show: false } },
  colors: ['#0F6E56', '#185FA5'],
  plotOptions: { pie: { donut: { size: '70%' } } },
  dataLabels: { enabled: false },
  stroke: { show: false },
  legend: { show: false },
  tooltip: { theme: 'dark', y: { formatter: (v) => formatCLP(v) } }
}

const cargarMeses = async () => {
  const res = await mesesService.getAll()
  meses.value = res.data
  if (meses.value.length > 0) {
    mesSeleccionado.value = meses.value[meses.value.length - 1].id
    await cargarResumen()
  }
}

const cargarResumen = async () => {
  if (!mesSeleccionado.value) return
  try {
    const res = await mesesService.getResumen(mesSeleccionado.value)
    resumen.value = res.data
    const cat = await gastosService.porCategoria(mesSeleccionado.value)
    gastosCat.value = cat.data
  } catch {
    resumen.value = null
    gastosCat.value = {}
  }
}

const crearMes = async () => {
  await mesesService.crear(nuevoAnio.value, nuevoMes.value)
  mostrarModalNuevoMes.value = false
  await cargarMeses()
}

const cerrarMes = async () => {
  if (!sueldoReal.value) return
  await mesesService.cerrar(mesSeleccionado.value, sueldoReal.value, sueldoBrutoReal.value || null)
  await cargarResumen()
  sueldoReal.value = ''
  sueldoBrutoReal.value = ''
}

onMounted(cargarMeses)
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
.metric-card { background: var(--bg-metric); border-radius: 10px; padding: 14px; transition: all 0.3s ease; }
.metric-label { font-size: 11px; color: var(--text-secondary); margin-bottom: 6px; }
.metric-val { font-size: 20px; font-weight: 600; color: var(--text-primary); }
.metric-val.red { color: #993C1D; }
.metric-val.blue { color: #185FA5; }
.metric-val.green { color: #0F6E56; }

/* NUEVOS ESTILOS PARA ALERTA */
.metric-card.is-critical {
  border: 1px solid #993C1D;
  background: rgba(153, 60, 29, 0.05) !important;
  animation: pulse-border 2s infinite;
}

.mini-alert {
  font-size: 10px;
  background: #993C1D;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  vertical-align: middle;
  margin-left: 5px;
}

@keyframes pulse-border {
  0% { box-shadow: 0 0 0 0 rgba(153, 60, 29, 0.4); }
  70% { box-shadow: 0 0 0 6px rgba(153, 60, 29, 0); }
  100% { box-shadow: 0 0 0 0 rgba(153, 60, 29, 0); }
}

.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 16px; }
.card-title { font-size: 11px; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 14px; }
.section-label { font-size: 11px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.4px; margin-bottom: 6px; padding: 6px 0 2px; border-bottom: 1px solid var(--border); }
.breakdown-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--border-light); font-size: 13px; color: var(--text-primary); }
.breakdown-row:last-child { border-bottom: none; }
.breakdown-row.total { font-weight: 600; font-size: 14px; }
.lbl { color: var(--text-secondary); }
.neg { color: #993C1D; }
.pos { color: #0F6E56; }
.blue { color: #185FA5; }
.green { color: #0F6E56; }
.aviso-mes { margin-top: 14px; padding: 12px; background: var(--bg-metric); border-radius: 8px; font-size: 13px; color: var(--text-secondary); text-align: center; }
.cerrar-desc { font-size: 13px; color: #888; margin-bottom: 12px; }
.form-row { display: flex; gap: 12px; flex-wrap: wrap; }
.form-group { flex: 1; min-width: 160px; }
.form-group label { font-size: 12px; color: var(--text-secondary); display: block; margin-bottom: 4px; }
.bar-group { margin-bottom: 10px; }
.bar-label { display: flex; justify-content: space-between; font-size: 12px; color: var(--text-secondary); margin-bottom: 5px; }
.bar-track { background: var(--bg-metric); border-radius: 4px; height: 8px; overflow: hidden; }
.bar-fill { background: #1D9E75; height: 100%; border-radius: 4px; }
.empty-state { font-size: 13px; color: var(--text-muted); text-align: center; padding: 20px 0; }
.empty-state-big { text-align: center; padding: 60px 20px; color: var(--text-muted); font-size: 14px; line-height: 2; }
.input { width: 100%; padding: 8px 12px; border: 1px solid var(--border); border-radius: 8px; font-size: 13px; background: var(--bg-card); color: var(--text-primary); }
.btn-primary { padding: 8px 16px; background: #185FA5; color: #fff; border: none; border-radius: 8px; font-size: 13px; cursor: pointer; white-space: nowrap; }
.btn-primary:hover { background: #0C447C; }
.btn-secondary { padding: 8px 16px; background: var(--bg-card); color: var(--text-primary); border: 1px solid var(--border); border-radius: 8px; font-size: 13px; cursor: pointer; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 200; }
.modal { background: var(--bg-card); border-radius: 14px; padding: 24px; width: 320px; }
.modal-title { font-size: 15px; font-weight: 600; margin-bottom: 16px; color: var(--text-primary); }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 16px; }
.donut-chart-wrapper { display: flex; justify-content: center; }
.donut-legend { display: flex; flex-direction: column; gap: 8px; }
.legend-item { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--text-primary); }
.legend-dot { width: 12px; height: 12px; border-radius: 50%; }
.top-cat-row { display: flex; justify-content: space-between; padding: 6px 0; font-size: 12px; border-bottom: 1px solid var(--border-light); }
.top-cat-row:last-child { border-bottom: none; }
.cat-name { color: var(--text-secondary); }
.cat-monto { font-weight: 600; color: var(--text-primary); }

@media (max-width: 768px) {
  .metrics-row { grid-template-columns: 1fr 1fr; }
  .two-col { grid-template-columns: 1fr; }
}
</style>
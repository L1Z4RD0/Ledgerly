<template>
  <div class="view">
    <div class="topbar">
      <div>
        <div class="topbar-title">Estadísticas Globales</div>
        <div class="topbar-sub">Análisis de rendimiento y ahorro mensual</div>
      </div>
    </div>

    <div class="page-content">
      <div class="metrics-row">
        <div class="metric-card">
          <div class="metric-label">Promedio Neto Mensual</div>
          <div class="metric-val">{{ formatCLP(promedioNeto) }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Mejor Mes (Saldo Libre)</div>
          <div class="metric-val blue">{{ formatCLP(mejorMes) }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Promedio de Gastos</div>
          <div class="metric-val red">{{ formatCLP(promedioGastos) }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Tasa de Ahorro Promedio</div>
          <div class="metric-val green">{{ saveRate }}%</div>
        </div>
      </div>

      <div class="two-col">
        <div class="card">
          <div class="card-title">Tendencia: Ingresos vs Gastos</div>
          <div v-if="resumenes.length === 0" class="empty-state">Sin datos aún</div>
          <apexchart v-else type="area" height="280" :options="chartOptions" :series="chartSeries"></apexchart>
        </div>

        <div class="card">
          <div class="card-title">Distribución de Gastos</div>
          <div v-if="Object.keys(gastosCatTotal).length === 0" class="empty-state">Sin gastos registrados</div>
          <apexchart v-else type="donut" height="280" :options="donutOptions" :series="donutSeries"></apexchart>
        </div>

        <div class="card">
          <div class="card-title">Comparativa: Ingreso vs Saldo Libre</div>
          <div v-if="resumenes.length === 0" class="empty-state">Esperando datos...</div>
          <apexchart v-else type="bar" height="280" :options="compareOptions" :series="compareSeries"></apexchart>
        </div>

        <div class="card">
          <div class="card-title">Eficiencia de Ahorro (KPI)</div>
          <div v-if="resumenesCerrados.length === 0" class="empty-state">Cierra un mes para ver tu eficiencia</div>
          <apexchart v-else type="radialBar" height="280" :options="saveOptions" :series="[saveRate]"></apexchart>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Historial Detallado</div>
        <div v-if="resumenes.length === 0" class="empty-state">No hay registros</div>
        <div v-else class="table-container">
          <div class="tabla-header">
            <span>Mes</span>
            <span>Ingresos</span>
            <span>Extras</span>
            <span>Gastos</span>
            <span>Deudas</span>
            <span>Saldo Libre</span>
          </div>
          <div v-for="r in resumenes" :key="r.mes_id" class="tabla-row">
            <span class="mes-label">{{ nombreMes(r.mes) }} {{ r.anio }}</span>
            <span>{{ formatCLP(r.sueldo_real || r.neto_estimado) }}</span>
            <span class="green">+{{ formatCLP(r.total_extras) }}</span>
            <span class="red">−{{ formatCLP(r.total_gastos) }}</span>
            <span class="red">−{{ formatCLP(r.total_pagos_deuda) }}</span>
            <span class="blue font-bold">{{ r.saldo_libre !== null ? formatCLP(r.saldo_libre) : 'En curso' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { mesesService, gastosService, ahorrosService } from '../services/api'

// --- ESTADO ---
const meses = ref([])
const resumenes = ref([])
const gastosCatTotal = ref({})
const ahorros = ref([])

// --- UTILIDADES ---
const nombresMeses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
const nombreMes = (n) => nombresMeses[n - 1]
const formatCLP = (n) => '$' + Math.round(n || 0).toLocaleString('es-CL')

const resumenesCerrados = computed(() => resumenes.value.filter(r => r.sueldo_real))

// --- MÉTRICAS ---
const promedioNeto = computed(() => {
  const cerrados = resumenesCerrados.value
  return cerrados.length ? cerrados.reduce((acc, r) => acc + (r.sueldo_real || 0), 0) / cerrados.length : 0
})

const mejorMes = computed(() => {
  const cerrados = resumenesCerrados.value
  return cerrados.length ? Math.max(...cerrados.map(r => r.saldo_libre || 0)) : 0
})

const promedioGastos = computed(() => {
  return resumenes.value.length ? resumenes.value.reduce((acc, r) => acc + (r.total_gastos || 0), 0) / resumenes.value.length : 0
})

// --- 1. CONFIG AREA CHART (TENDENCIAS) ---
const chartSeries = computed(() => [
  { name: 'Ingresos Totales', data: resumenes.value.map(r => (r.sueldo_real || r.neto_estimado || 0) + (r.total_extras || 0)) },
  { name: 'Gastos', data: resumenes.value.map(r => r.total_gastos || 0) }
])

const chartOptions = computed(() => ({
  chart: { toolbar: { show: false }, zoom: { enabled: false }, fontFamily: 'inherit' },
  colors: ['#185FA5', '#993C1D'],
  stroke: { curve: 'smooth', width: 3 },
  fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.4, opacityTo: 0.05 } },
  xaxis: { categories: resumenes.value.map(r => nombreMes(r.mes)), labels: { style: { colors: '#888' } } },
  yaxis: { labels: { formatter: (v) => formatCLP(v), style: { colors: '#888' } } },
  dataLabels: { enabled: false },
  grid: { borderColor: '#f0f0ee' },
  tooltip: { theme: 'dark' }
}))

// --- 2. CONFIG DONUT CHART (GASTOS) ---
const donutSeries = computed(() => Object.values(gastosCatTotal.value))
const donutOptions = computed(() => ({
  labels: Object.keys(gastosCatTotal.value),
  chart: { fontFamily: 'inherit' },
  colors: ['#185FA5', '#1D9E75', '#993C1D', '#F59E0B', '#6366F1'],
  legend: { position: 'bottom', labels: { colors: '#888' } },
  plotOptions: { pie: { donut: { size: '65%' } } },
  stroke: { show: false },
  tooltip: { theme: 'dark' }
}))

// --- 3. CONFIG GROUPED BAR CHART (COMPARATIVA INGRESO VS AHORRO) ---
const compareSeries = computed(() => [
  {
    name: 'Ingreso Total',
    data: resumenes.value.map(r => (r.sueldo_real || r.neto_estimado || 0) + (r.total_extras || 0))
  },
  {
    name: 'Saldo Libre (Ahorro)',
    data: resumenes.value.map(r => r.saldo_libre || 0)
  }
])

const compareOptions = computed(() => ({
  chart: { type: 'bar', fontFamily: 'inherit', toolbar: { show: false } },
  colors: ['#185FA5', '#0F6E56'], // Azul para ingreso, Verde para ahorro
  plotOptions: {
    bar: {
      horizontal: false,
      columnWidth: '55%',
      borderRadius: 4
    }
  },
  dataLabels: { enabled: false },
  stroke: { show: true, width: 2, colors: ['transparent'] },
  xaxis: {
    categories: resumenes.value.map(r => nombreMes(r.mes)),
    labels: { style: { colors: '#888' } }
  },
  yaxis: { labels: { formatter: (v) => formatCLP(v), style: { colors: '#888' } } },
  fill: { opacity: 1 },
  tooltip: { theme: 'dark', y: { formatter: (v) => formatCLP(v) } },
  grid: { borderColor: '#f0f0ee' }
}))

// --- 4. CONFIG RADIAL BAR (TASA DE AHORRO) ---
const saveRate = computed(() => {
  const cerrados = resumenesCerrados.value
  const ingresos = cerrados.reduce((acc, r) => acc + (r.sueldo_real + r.total_extras), 0)
  const ahorroMeses = cerrados.reduce((acc, r) => acc + (r.saldo_libre || 0), 0)
  const ahorroModulo = ahorros.value.reduce((acc, a) => acc + a.monto_actual, 0)
  const totalAhorro = ahorroMeses + ahorroModulo
  return ingresos > 0 ? Math.round((totalAhorro / ingresos) * 100) : 0
})

const saveOptions = {
  plotOptions: {
    radialBar: {
      hollow: { size: '70%' },
      dataLabels: {
        name: { show: true, color: '#888', fontSize: '12px' },
        value: { color: '#0F6E56', fontSize: '24px', fontWeight: '700', formatter: (v) => v + '%' }
      }
    }
  },
  colors: ['#0F6E56'],
  labels: ['Eficiencia de Ahorro']
}

// --- CARGA DE DATOS ---
const cargarDatos = async () => {
  // Cargar ahorros
  try {
    const resAhorros = await ahorrosService.getActivos()
    ahorros.value = resAhorros.data
  } catch { /* sin ahorros */ }

  // Cargar meses y resumenes
  const res = await mesesService.getAll()
  meses.value = res.data
  const resList = []
  const catAcum = {}
  for (const m of meses.value) {
    try {
      const r = await mesesService.getResumen(m.id)
      resList.push(r.data)
      const cats = await gastosService.porCategoria(m.id)
      for (const [cat, monto] of Object.entries(cats.data)) {
        catAcum[cat] = (catAcum[cat] || 0) + monto
      }
    } catch { /* mes sin datos */ }
  }
  resumenes.value = resList
  gastosCatTotal.value = catAcum
}

onMounted(cargarDatos)
</script>

<style scoped>
/* (Se mantienen los estilos anteriores) */
.view { min-height: 100vh; background: #f5f5f3; }
.topbar { padding: 16px 24px; background: #fff; border-bottom: 1px solid #e5e5e3; }
.topbar-title { font-size: 16px; font-weight: 600; }
.topbar-sub { font-size: 12px; color: #888; margin-top: 2px; }
.page-content { padding: 20px 24px; display: flex; flex-direction: column; gap: 20px; }
.metrics-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.metric-card { background: #efefed; border-radius: 12px; padding: 16px; }
.metric-label { font-size: 11px; color: #888; text-transform: uppercase; margin-bottom: 8px; }
.metric-val { font-size: 20px; font-weight: 600; }
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.card { background: #fff; border: 1px solid #e5e5e3; border-radius: 14px; padding: 20px; }
.card-title { font-size: 11px; font-weight: 700; color: #aaa; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 16px; }
.green { color: #0F6E56; }
.red { color: #993C1D; }
.blue { color: #185FA5; }
.font-bold { font-weight: 600; }
.empty-state { font-size: 13px; color: #aaa; text-align: center; padding: 40px 0; }
.table-container { overflow-x: auto; }
.tabla-header { display: grid; grid-template-columns: 1.2fr 1fr 1fr 1fr 1fr 1fr; gap: 10px; font-size: 11px; color: #aaa; text-transform: uppercase; padding-bottom: 10px; border-bottom: 1px solid #eee; }
.tabla-row { display: grid; grid-template-columns: 1.2fr 1fr 1fr 1fr 1fr 1fr; gap: 10px; font-size: 13px; padding: 12px 0; border-bottom: 1px solid #f9f9f9; }
.mes-label { font-weight: 500; color: #444; }

@media (max-width: 768px) {
  .metrics-row { grid-template-columns: 1fr 1fr; }
  .two-col { grid-template-columns: 1fr; }
  .tabla-header, .tabla-row { grid-template-columns: 1fr 1fr 1fr; }
  .tabla-header span:nth-child(n+4), .tabla-row span:nth-child(n+4) { display: none; }
}
</style>
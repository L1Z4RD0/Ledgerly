<template>
  <div class="view">
    <div class="topbar">
      <div>
        <div class="topbar-title">Estadísticas</div>
        <div class="topbar-sub">Comparativa de todos los meses</div>
      </div>
    </div>

    <div class="page-content">
      <div class="metrics-row">
        <div class="metric-card">
          <div class="metric-label">Promedio neto mensual</div>
          <div class="metric-val">{{ formatCLP(promedioNeto) }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Mejor mes</div>
          <div class="metric-val blue">{{ formatCLP(mejorMes) }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Promedio gastos</div>
          <div class="metric-val red">{{ formatCLP(promedioGastos) }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Ahorro promedio</div>
          <div class="metric-val green">{{ formatCLP(promedioAhorro) }}</div>
        </div>
      </div>

      <div class="two-col">
        <div class="card">
          <div class="card-title">Neto por mes</div>
          <div v-if="resumenes.length === 0" class="empty-state">Sin datos aún</div>
          <div v-for="r in resumenes" :key="r.mes_id" class="bar-group">
            <div class="bar-label">
              <span>{{ nombreMes(r.mes) }} {{ r.anio }}</span>
              <span>{{ r.saldo_libre !== null ? formatCLP(r.saldo_libre) : 'En curso' }}</span>
            </div>
            <div class="bar-track">
              <div class="bar-fill blue" :style="{ width: pctNeto(r.saldo_libre) + '%' }"></div>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-title">Estimado vs real</div>
          <div v-if="resumenesCerrados.length === 0" class="empty-state">Sin meses cerrados aún</div>
          <div v-for="r in resumenesCerrados" :key="r.mes_id" class="bar-group">
            <div class="bar-label">
              <span>{{ nombreMes(r.mes) }} — estimado</span>
              <span>{{ formatCLP(r.bruto) }}</span>
            </div>
            <div class="bar-track">
              <div class="bar-fill light-blue" :style="{ width: pctBruto(r.bruto) + '%' }"></div>
            </div>
            <div class="bar-label" style="margin-top:4px">
              <span>{{ nombreMes(r.mes) }} — real</span>
              <span :class="r.sueldo_real >= r.bruto ? 'green' : 'red'">{{ formatCLP(r.sueldo_real) }}</span>
            </div>
            <div class="bar-track">
              <div class="bar-fill blue" :style="{ width: pctBruto(r.sueldo_real) + '%' }"></div>
            </div>
            <div class="diferencia-row">
              <span class="lbl">Diferencia</span>
              <span :class="r.diferencia >= 0 ? 'green' : 'red'">
                {{ r.diferencia >= 0 ? '+' : '' }}{{ formatCLP(r.diferencia) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Gastos por categoría — acumulado</div>
        <div v-if="Object.keys(gastosCatTotal).length === 0" class="empty-state">Sin gastos registrados aún</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px 24px;">
          <div v-for="(monto, cat) in gastosCatTotal" :key="cat" class="bar-group">
            <div class="bar-label">
              <span>{{ cat }}</span>
              <span>{{ formatCLP(monto) }}</span>
            </div>
            <div class="bar-track">
              <div class="bar-fill green" :style="{ width: pctCat(monto) + '%' }"></div>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Resumen por mes</div>
        <div v-if="resumenes.length === 0" class="empty-state">Sin datos aún</div>
        <div v-else>
          <div class="tabla-header">
            <span>Mes</span>
            <span>Bruto est.</span>
            <span>Líquido real</span>
            <span>Extras</span>
            <span>Gastos</span>
            <span>Pagos deuda</span>
            <span>Saldo libre</span>
          </div>
          <div v-for="r in resumenes" :key="r.mes_id" class="tabla-row">
            <span class="mes-label">{{ nombreMes(r.mes) }} {{ r.anio }}</span>
            <span>{{ formatCLP(r.bruto) }}</span>
            <span>{{ r.sueldo_real ? formatCLP(r.sueldo_real) : '—' }}</span>
            <span class="green">{{ r.total_extras > 0 ? '+' + formatCLP(r.total_extras) : '—' }}</span>
            <span class="red">{{ r.total_gastos > 0 ? '−' + formatCLP(r.total_gastos) : '—' }}</span>
            <span class="red">{{ r.total_pagos_deuda > 0 ? '−' + formatCLP(r.total_pagos_deuda) : '—' }}</span>
            <span class="blue font-bold">{{ r.saldo_libre !== null ? formatCLP(r.saldo_libre) : 'En curso' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { mesesService, gastosService } from '../services/api'

const meses = ref([])
const resumenes = ref([])
const gastosCatTotal = ref({})

const nombresMeses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
const nombreMes = (n) => nombresMeses[n - 1]
const formatCLP = (n) => '$' + Math.round(n || 0).toLocaleString('es-CL')

const resumenesCerrados = computed(() => resumenes.value.filter(r => r.sueldo_real))

const promedioNeto = computed(() => {
  const cerrados = resumenesCerrados.value
  if (!cerrados.length) return 0
  return cerrados.reduce((acc, r) => acc + (r.sueldo_real || 0), 0) / cerrados.length
})

const mejorMes = computed(() => {
  const cerrados = resumenesCerrados.value
  return cerrados.length ? Math.max(...cerrados.map(r => r.saldo_libre || 0)) : 0
})

const promedioGastos = computed(() => {
  if (!resumenes.value.length) return 0
  return resumenes.value.reduce((acc, r) => acc + (r.total_gastos || 0), 0) / resumenes.value.length
})

const promedioAhorro = computed(() => {
  const cerrados = resumenesCerrados.value
  if (!cerrados.length) return 0
  return cerrados.reduce((acc, r) => acc + (r.saldo_libre || 0), 0) / cerrados.length
})

const maxSaldo = computed(() => {
  const vals = resumenes.value.map(r => r.saldo_libre || 0)
  return vals.length ? Math.max(...vals, 1) : 1
})

const maxBruto = computed(() => {
  const vals = resumenes.value.map(r => Math.max(r.bruto || 0, r.sueldo_real || 0))
  return vals.length ? Math.max(...vals, 1) : 1
})

const maxCat = computed(() => {
  const vals = Object.values(gastosCatTotal.value)
  return vals.length ? Math.max(...vals, 1) : 1
})

const pctNeto = (n) => Math.round(((n || 0) / maxSaldo.value) * 100)
const pctBruto = (n) => Math.round(((n || 0) / maxBruto.value) * 100)
const pctCat = (n) => Math.round(((n || 0) / maxCat.value) * 100)

const cargarDatos = async () => {
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
    } catch (e) { // eslint-disable-line no-unused-vars
      // mes sin datos
    }
  }
  resumenes.value = resList
  gastosCatTotal.value = catAcum
}

onMounted(cargarDatos)
</script>

<style scoped>
.view { min-height: 100vh; background: #f5f5f3; }
.topbar { padding: 16px 24px; background: #fff; border-bottom: 1px solid #e5e5e3; display: flex; align-items: center; justify-content: space-between; }
.topbar-title { font-size: 16px; font-weight: 600; }
.topbar-sub { font-size: 12px; color: #888; margin-top: 2px; }
.page-content { padding: 20px 24px; display: flex; flex-direction: column; gap: 16px; }
.metrics-row { display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 12px; }
.metric-card { background: #efefed; border-radius: 10px; padding: 14px; }
.metric-label { font-size: 11px; color: #888; margin-bottom: 6px; }
.metric-val { font-size: 20px; font-weight: 600; }
.metric-val.blue { color: #185FA5; }
.metric-val.red { color: #993C1D; }
.metric-val.green { color: #0F6E56; }
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.card { background: #fff; border: 1px solid #e5e5e3; border-radius: 12px; padding: 16px; }
.card-title { font-size: 11px; font-weight: 600; color: #888; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 14px; }
.bar-group { margin-bottom: 12px; }
.bar-label { display: flex; justify-content: space-between; font-size: 12px; color: #888; margin-bottom: 5px; }
.bar-track { background: #efefed; border-radius: 4px; height: 8px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 4px; }
.bar-fill.blue { background: #185FA5; }
.bar-fill.light-blue { background: #B5D4F4; }
.bar-fill.green { background: #1D9E75; }
.diferencia-row { display: flex; justify-content: space-between; font-size: 12px; padding: 6px 0 2px; border-top: 1px solid #f0f0ee; margin-top: 6px; }
.lbl { color: #888; }
.green { color: #0F6E56; }
.red { color: #993C1D; }
.blue { color: #185FA5; }
.font-bold { font-weight: 600; }
.empty-state { font-size: 13px; color: #aaa; text-align: center; padding: 20px 0; }
.tabla-header { display: grid; grid-template-columns: 1.5fr 1fr 1fr 1fr 1fr 1fr 1fr; gap: 8px; font-size: 11px; color: #aaa; text-transform: uppercase; letter-spacing: 0.4px; padding-bottom: 8px; border-bottom: 1px solid #e5e5e3; }
.tabla-row { display: grid; grid-template-columns: 1.5fr 1fr 1fr 1fr 1fr 1fr 1fr; gap: 8px; font-size: 13px; padding: 10px 0; border-bottom: 1px solid #f0f0ee; }
.tabla-row:last-child { border-bottom: none; }
.mes-label { font-weight: 500; }

@media (max-width: 768px) {
  .metrics-row { grid-template-columns: 1fr 1fr; }
  .two-col { grid-template-columns: 1fr; }
  .tabla-header, .tabla-row { grid-template-columns: 1fr 1fr 1fr; }
  .tabla-header span:nth-child(n+4), .tabla-row span:nth-child(n+4) { display: none; }
}
</style>
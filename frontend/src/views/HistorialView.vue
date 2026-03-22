<template>
  <div class="view">
    <div class="topbar">
      <div>
        <div class="topbar-title">Historial</div>
        <div class="topbar-sub">Todos los meses registrados</div>
      </div>
    </div>

    <div class="page-content">
      <div class="metrics-row">
        <div class="metric-card">
          <div class="metric-label">Meses registrados</div>
          <div class="metric-val">{{ meses.length }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Meses cerrados</div>
          <div class="metric-val">{{ mesesCerrados }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Mejor saldo libre</div>
          <div class="metric-val green">{{ formatCLP(mejorSaldo) }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Total ahorrado</div>
          <div class="metric-val blue">{{ formatCLP(totalAhorrado) }}</div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Historial mensual</div>
        <div v-if="resumenes.length === 0" class="empty-state">Sin meses registrados aún</div>
        <div v-else>
          <div class="hist-header">
            <span>Mes</span>
            <span>Bruto est.</span>
            <span>Líquido real</span>
            <span>Pagos deuda</span>
            <span>Extras</span>
            <span>Gastos</span>
            <span>Saldo libre</span>
            <span>Estado</span>
          </div>
          <div v-for="r in resumenes" :key="r.mes_id" class="hist-row">
            <span class="mes-label">{{ nombreMes(r.mes) }} {{ r.anio }}</span>
            <span>{{ formatCLP(r.bruto) }}</span>
            <span>{{ r.sueldo_real ? formatCLP(r.sueldo_real) : '—' }}</span>
            <span class="red">{{ r.total_pagos_deuda > 0 ? '−' + formatCLP(r.total_pagos_deuda) : '—' }}</span>
            <span class="green">{{ r.total_extras > 0 ? '+' + formatCLP(r.total_extras) : '—' }}</span>
            <span class="red">{{ r.total_gastos > 0 ? '−' + formatCLP(r.total_gastos) : '—' }}</span>
            <span class="blue font-bold">{{ r.saldo_libre !== null ? formatCLP(r.saldo_libre) : 'En curso' }}</span>
            <span>
              <span v-if="r.mes_cerrado" class="badge-ok">Cerrado</span>
              <span v-else class="badge-pending">En curso</span>
            </span>
          </div>
        </div>
      </div>

      <div v-for="r in resumenes" :key="'card-' + r.mes_id" class="card">
        <div class="card-header">
          <div>
            <div class="card-mes">{{ nombreMes(r.mes) }} {{ r.anio }}</div>
            <div class="card-sub">{{ r.mes_cerrado ? 'Mes cerrado' : 'En curso' }}</div>
          </div>
          <span v-if="r.mes_cerrado" class="badge-ok">Cerrado</span>
          <span v-else class="badge-pending">En curso</span>
        </div>
        <div class="hist-detail">
          <div class="section-label">Estimación</div>
          <div class="detail-row">
            <span class="lbl">Bruto estimado</span>
            <span>{{ formatCLP(r.bruto) }}</span>
          </div>
          <div class="detail-row">
            <span class="lbl">AFP (10,46%)</span>
            <span class="red">−{{ formatCLP(r.descuento_afp) }}</span>
          </div>
          <div class="detail-row">
            <span class="lbl">Fonasa (7%)</span>
            <span class="red">−{{ formatCLP(r.descuento_fonasa) }}</span>
          </div>
          <div class="detail-row total">
            <span>Neto estimado</span>
            <span class="blue">{{ formatCLP(r.neto_estimado) }}</span>
          </div>

          <template v-if="r.mes_cerrado">
            <div class="section-label" style="margin-top:12px">Real</div>
            <div class="detail-row">
              <span class="lbl">Saldo mes anterior</span>
              <span class="green">+{{ formatCLP(r.saldo_anterior) }}</span>
            </div>
            <div class="detail-row">
              <span class="lbl">Líquido recibido</span>
              <span class="green">+{{ formatCLP(r.sueldo_real) }}</span>
            </div>
            <div class="detail-row" v-if="r.total_extras > 0">
              <span class="lbl">Ingresos extra</span>
              <span class="green">+{{ formatCLP(r.total_extras) }}</span>
            </div>
            <div class="detail-row" v-if="r.total_pagos_deuda > 0">
              <span class="lbl">Pagos de deudas</span>
              <span class="red">−{{ formatCLP(r.total_pagos_deuda) }}</span>
            </div>
            <div class="detail-row" v-if="r.total_gastos > 0">
              <span class="lbl">Gastos registrados</span>
              <span class="red">−{{ formatCLP(r.total_gastos) }}</span>
            </div>
            <div class="detail-row total">
              <span>Saldo libre final</span>
              <span class="green">{{ formatCLP(r.saldo_libre) }}</span>
            </div>
            <div class="detail-row" v-if="r.diferencia_bruto !== null">
              <span class="lbl">Diferencia estimado/real</span>
              <span :class="r.diferencia_bruto >= 0 ? 'green' : 'red'">
                {{ r.diferencia_bruto >= 0 ? '+' : '' }}{{ formatCLP(r.diferencia_bruto) }}
              </span>
            </div>
          </template>

          <template v-else>
            <div class="section-label" style="margin-top:12px">Disponible ahora</div>
            <div class="detail-row">
              <span class="lbl">Saldo anterior</span>
              <span class="green">{{ formatCLP(r.saldo_anterior) }}</span>
            </div>
            <div class="detail-row" v-if="r.total_extras > 0">
              <span class="lbl">Ingresos extra</span>
              <span class="green">+{{ formatCLP(r.total_extras) }}</span>
            </div>
            <div class="detail-row" v-if="r.total_gastos > 0">
              <span class="lbl">Gastos registrados</span>
              <span class="red">−{{ formatCLP(r.total_gastos) }}</span>
            </div>
            <div class="detail-row" v-if="r.total_pagos_deuda > 0">
              <span class="lbl">Pagos de deudas</span>
              <span class="red">−{{ formatCLP(r.total_pagos_deuda) }}</span>
            </div>
            <div class="detail-row total">
              <span>Disponible ahora</span>
              <span class="blue">{{ formatCLP(r.saldo_disponible) }}</span>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { mesesService } from '../services/api'

const meses = ref([])
const resumenes = ref([])

const nombresMeses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
const nombreMes = (n) => nombresMeses[n - 1]
const formatCLP = (n) => '$' + Math.round(n || 0).toLocaleString('es-CL')

const mesesCerrados = computed(() => resumenes.value.filter(r => r.mes_cerrado).length)
const mejorSaldo = computed(() => {
  const vals = resumenes.value.filter(r => r.saldo_libre !== null).map(r => r.saldo_libre)
  return vals.length ? Math.max(...vals) : 0
})
const totalAhorrado = computed(() => {
  const ultimo = resumenes.value.find(r => r.saldo_libre !== null)
  return ultimo ? ultimo.saldo_libre : 0
})

const cargarDatos = async () => {
  const res = await mesesService.getAll()
  meses.value = res.data
  const resList = []
  for (const m of meses.value) {
    try {
      const r = await mesesService.getResumen(m.id)
      resList.push(r.data)
    } catch (e) { // eslint-disable-line no-unused-vars
      // mes sin datos
    }
  }
  resumenes.value = resList.reverse()
}

onMounted(cargarDatos)
</script>

<style scoped>
.view { min-height: 100vh; background: var(--bg); color: var(--text-primary); }
.topbar { padding: 16px 24px; background: var(--bg-card); border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; }
.topbar-title { font-size: 16px; font-weight: 600; color: var(--text-primary); }
.topbar-sub { font-size: 12px; color: var(--text-secondary); margin-top: 2px; }
.page-content { padding: 20px 24px; display: flex; flex-direction: column; gap: 16px; }
.metrics-row { display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 12px; }
.metric-card { background: var(--bg-metric); border-radius: 10px; padding: 14px; }
.metric-label { font-size: 11px; color: var(--text-secondary); margin-bottom: 6px; }
.metric-val { font-size: 20px; font-weight: 600; color: var(--text-primary); }
.metric-val.green { color: #0F6E56; }
.metric-val.blue { color: #185FA5; }
.card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 16px; }
.card-title { font-size: 11px; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 14px; }
.card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 14px; }
.card-mes { font-size: 15px; font-weight: 600; color: var(--text-primary); }
.card-sub { font-size: 12px; color: var(--text-secondary); margin-top: 2px; }
.section-label { font-size: 11px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.4px; padding: 6px 0 2px; border-bottom: 1px solid var(--border); margin-bottom: 4px; }
.hist-header { display: grid; grid-template-columns: 1.5fr 1fr 1fr 1fr 1fr 1fr 1fr 80px; gap: 8px; font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.4px; padding-bottom: 8px; border-bottom: 1px solid var(--border); }
.hist-row { display: grid; grid-template-columns: 1.5fr 1fr 1fr 1fr 1fr 1fr 1fr 80px; gap: 8px; font-size: 13px; padding: 10px 0; border-bottom: 1px solid var(--border-light); align-items: center; color: var(--text-primary); }
.hist-row:last-child { border-bottom: none; }
.mes-label { font-weight: 500; }
.hist-detail { display: flex; flex-direction: column; }
.detail-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--border-light); font-size: 13px; color: var(--text-primary); }
.detail-row:last-child { border-bottom: none; }
.detail-row.total { font-weight: 600; font-size: 14px; }
.lbl { color: var(--text-secondary); }
.green { color: #0F6E56; }
.red { color: #993C1D; }
.blue { color: #185FA5; }
.muted { color: var(--text-muted); }
.font-bold { font-weight: 600; }
.badge-ok { background: #EAF3DE; color: #3B6D11; font-size: 11px; padding: 4px 10px; border-radius: 6px; font-weight: 500; }
.badge-pending { background: #FAEEDA; color: #854F0B; font-size: 11px; padding: 4px 10px; border-radius: 6px; font-weight: 500; }
.empty-state { font-size: 13px; color: var(--text-muted); text-align: center; padding: 20px 0; }

@media (max-width: 768px) {
  .metrics-row { grid-template-columns: 1fr 1fr; }
  .hist-header, .hist-row { grid-template-columns: 1fr 1fr 1fr; }
  .hist-header span:nth-child(n+4), .hist-row span:nth-child(n+4) { display: none; }
}
</style>
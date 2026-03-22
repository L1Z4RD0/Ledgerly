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
          <div class="metric-label">Mejor diferencia</div>
          <div class="metric-val green">{{ formatCLP(mejorDiferencia) }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Peor diferencia</div>
          <div class="metric-val red">{{ formatCLP(peorDiferencia) }}</div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Historial mensual</div>
        <div v-if="resumenes.length === 0" class="empty-state">Sin meses registrados aún</div>
        <div v-else>
          <div class="hist-header">
            <span>Mes</span>
            <span>Estimado</span>
            <span>Real recibido</span>
            <span>Gastos</span>
            <span>Saldo libre</span>
            <span>Diferencia</span>
            <span>Estado</span>
          </div>
          <div v-for="r in resumenes" :key="r.mes_id" class="hist-row">
            <span class="mes-label">{{ nombreMes(r.mes) }} {{ r.anio }}</span>
            <span>{{ formatCLP(r.bruto) }}</span>
            <span>{{ r.sueldo_real ? formatCLP(r.sueldo_real) : '—' }}</span>
            <span class="red">{{ r.total_gastos > 0 ? '−' + formatCLP(r.total_gastos) : '—' }}</span>
            <span class="blue font-bold">{{ formatCLP(r.saldo_libre) }}</span>
            <span v-if="r.diferencia !== null" :class="r.diferencia >= 0 ? 'green' : 'red'">
              {{ r.diferencia >= 0 ? '+' : '' }}{{ formatCLP(r.diferencia) }}
            </span>
            <span v-else class="muted">—</span>
            <span>
              <span v-if="r.sueldo_real" class="badge-ok">Cerrado</span>
              <span v-else class="badge-pending">En curso</span>
            </span>
          </div>
        </div>
      </div>

      <div v-for="r in resumenes" :key="'card-' + r.mes_id" class="card">
        <div class="card-header">
          <div>
            <div class="card-mes">{{ nombreMes(r.mes) }} {{ r.anio }}</div>
            <div class="card-sub">{{ r.sueldo_real ? 'Mes cerrado' : 'En curso' }}</div>
          </div>
          <span v-if="r.sueldo_real" class="badge-ok">Cerrado</span>
          <span v-else class="badge-pending">En curso</span>
        </div>
        <div class="hist-detail">
          <div class="detail-row">
            <span class="lbl">Bruto estimado</span>
            <span>{{ formatCLP(r.bruto) }}</span>
          </div>
          <div class="detail-row">
            <span class="lbl">AFP + Fonasa</span>
            <span class="red">−{{ formatCLP(r.descuento_afp + r.descuento_fonasa) }}</span>
          </div>
          <div class="detail-row">
            <span class="lbl">Deudas</span>
            <span class="red">−{{ formatCLP(r.total_deudas) }}</span>
          </div>
          <div class="detail-row">
            <span class="lbl">Ingresos extra</span>
            <span class="green">+{{ formatCLP(r.total_extras) }}</span>
          </div>
          <div class="detail-row">
            <span class="lbl">Gastos registrados</span>
            <span class="red">−{{ formatCLP(r.total_gastos) }}</span>
          </div>
          <div class="detail-row total">
            <span>Saldo libre</span>
            <span class="blue">{{ formatCLP(r.saldo_libre) }}</span>
          </div>
          <div v-if="r.sueldo_real" class="detail-row" style="margin-top:8px;padding-top:8px;border-top:1px solid #e5e5e3">
            <span class="lbl">Sueldo real recibido</span>
            <span>{{ formatCLP(r.sueldo_real) }}</span>
          </div>
          <div v-if="r.diferencia !== null" class="detail-row">
            <span class="lbl">Diferencia estimado/real</span>
            <span :class="r.diferencia >= 0 ? 'green' : 'red'">
              {{ r.diferencia >= 0 ? '+' : '' }}{{ formatCLP(r.diferencia) }}
            </span>
          </div>
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

const mesesCerrados = computed(() => resumenes.value.filter(r => r.sueldo_real).length)
const diferencias = computed(() => resumenes.value.filter(r => r.diferencia !== null).map(r => r.diferencia))
const mejorDiferencia = computed(() => diferencias.value.length ? Math.max(...diferencias.value) : 0)
const peorDiferencia = computed(() => diferencias.value.length ? Math.min(...diferencias.value) : 0)

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
.view { min-height: 100vh; background: #f5f5f3; }
.topbar { padding: 16px 24px; background: #fff; border-bottom: 1px solid #e5e5e3; display: flex; align-items: center; justify-content: space-between; }
.topbar-title { font-size: 16px; font-weight: 600; }
.topbar-sub { font-size: 12px; color: #888; margin-top: 2px; }
.page-content { padding: 20px 24px; display: flex; flex-direction: column; gap: 16px; }
.metrics-row { display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 12px; }
.metric-card { background: #efefed; border-radius: 10px; padding: 14px; }
.metric-label { font-size: 11px; color: #888; margin-bottom: 6px; }
.metric-val { font-size: 20px; font-weight: 600; }
.metric-val.green { color: #0F6E56; }
.metric-val.red { color: #993C1D; }
.card { background: #fff; border: 1px solid #e5e5e3; border-radius: 12px; padding: 16px; }
.card-title { font-size: 11px; font-weight: 600; color: #888; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 14px; }
.card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 14px; }
.card-mes { font-size: 15px; font-weight: 600; }
.card-sub { font-size: 12px; color: #888; margin-top: 2px; }
.hist-header { display: grid; grid-template-columns: 1.5fr 1fr 1fr 1fr 1fr 1fr 1fr; gap: 8px; font-size: 11px; color: #aaa; text-transform: uppercase; letter-spacing: 0.4px; padding-bottom: 8px; border-bottom: 1px solid #e5e5e3; }
.hist-row { display: grid; grid-template-columns: 1.5fr 1fr 1fr 1fr 1fr 1fr 1fr; gap: 8px; font-size: 13px; padding: 10px 0; border-bottom: 1px solid #f0f0ee; align-items: center; }
.hist-row:last-child { border-bottom: none; }
.mes-label { font-weight: 500; }
.hist-detail { display: flex; flex-direction: column; gap: 0; }
.detail-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f0f0ee; font-size: 13px; }
.detail-row:last-child { border-bottom: none; }
.detail-row.total { font-weight: 600; font-size: 14px; }
.lbl { color: #888; }
.green { color: #0F6E56; }
.red { color: #993C1D; }
.blue { color: #185FA5; }
.muted { color: #ccc; }
.font-bold { font-weight: 600; }
.badge-ok { background: #EAF3DE; color: #3B6D11; font-size: 11px; padding: 4px 10px; border-radius: 6px; font-weight: 500; }
.badge-pending { background: #FAEEDA; color: #854F0B; font-size: 11px; padding: 4px 10px; border-radius: 6px; font-weight: 500; }
.empty-state { font-size: 13px; color: #aaa; text-align: center; padding: 20px 0; }

@media (max-width: 768px) {
  .metrics-row { grid-template-columns: 1fr 1fr; }
  .hist-header, .hist-row { grid-template-columns: 1fr 1fr 1fr; }
  .hist-header span:nth-child(n+4), .hist-row span:nth-child(n+4) { display: none; }
}
</style>
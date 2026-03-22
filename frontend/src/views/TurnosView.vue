<template>
  <div class="view">
    <div class="topbar">
      <div>
        <div class="topbar-title">Turnos</div>
        <div class="topbar-sub">{{ mesLabel }}</div>
      </div>
      <select v-model="mesSeleccionado" @change="cargarTurnos" class="select-mes">
        <option v-for="m in meses" :key="m.id" :value="m.id">
          {{ nombreMes(m.mes) }} {{ m.anio }}
        </option>
      </select>
    </div>

    <div class="page-content">
      <div class="metrics-row">
        <div class="metric-card">
          <div class="metric-label">Total turnos</div>
          <div class="metric-val">{{ totalTurnos }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Valor por turno</div>
          <div class="metric-val">$16.000</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Horas totales</div>
          <div class="metric-val">{{ totalTurnos * 5 }} hrs</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Bruto estimado</div>
          <div class="metric-val blue">{{ formatCLP(totalTurnos * 16000) }}</div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Semanas del mes</div>
        <div v-for="s in semanas" :key="s.id" class="semana-row">
          <span class="semana-badge">Sem {{ s.numero_semana }}</span>
          <div class="semana-controls">
            <button @click="cambiarTurnos(s, -1)" class="btn-round">−</button>
            <span class="semana-turnos">{{ s.turnos }} turnos</span>
            <button @click="cambiarTurnos(s, 1)" class="btn-round">+</button>
          </div>
          <span class="semana-monto">{{ formatCLP(s.turnos * s.valor_turno) }}</span>
        </div>

        <div class="semana-total">
          <span>Total bruto estimado</span>
          <span class="blue">{{ formatCLP(totalTurnos * 16000) }}</span>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Agregar semana {{ proximaSemana }}</div>
        <div class="form-row">
          <div class="form-group">
            <label>Semana asignada automáticamente</label>
            <div class="semana-auto">Semana {{ proximaSemana }}</div>
          </div>
          <div class="form-group">
            <label>Turnos</label>
            <input v-model="nuevosTurnos" type="number" min="0" class="input" placeholder="Ej: 5" />
          </div>
          <div class="form-group">
            <label>Valor turno (CLP)</label>
            <input v-model="valorTurno" type="number" class="input" placeholder="16000" />
          </div>
          <button @click="agregarSemana" class="btn-primary" style="align-self:flex-end">Agregar</button>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Descuentos sobre el bruto</div>
        <div class="breakdown-row">
          <span class="lbl">AFP (10,46%)</span>
          <span class="neg">−{{ formatCLP(totalTurnos * 16000 * 0.1046) }}</span>
        </div>
        <div class="breakdown-row">
          <span class="lbl">Fonasa (7%)</span>
          <span class="neg">−{{ formatCLP(totalTurnos * 16000 * 0.07) }}</span>
        </div>
        <div class="breakdown-row total">
          <span>Neto tras descuentos legales</span>
          <span class="blue">{{ formatCLP(totalTurnos * 16000 * (1 - 0.1046 - 0.07)) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { mesesService, turnosService } from '../services/api'

const meses = ref([])
const mesSeleccionado = ref(null)
const semanas = ref([])
const nuevosTurnos = ref('')
const valorTurno = ref(16000)

const nombresMeses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
const nombreMes = (n) => nombresMeses[n - 1]

const mesLabel = computed(() => {
  if (!mesSeleccionado.value || !meses.value.length) return ''
  const m = meses.value.find(x => x.id === mesSeleccionado.value)
  return m ? `${nombreMes(m.mes)} ${m.anio}` : ''
})

const totalTurnos = computed(() => semanas.value.reduce((acc, s) => acc + s.turnos, 0))
const formatCLP = (n) => '$' + Math.round(n).toLocaleString('es-CL')

const proximaSemana = computed(() => {
  if (semanas.value.length === 0) return 1
  return Math.max(...semanas.value.map(s => s.numero_semana)) + 1
})

const cargarMeses = async () => {
  const res = await mesesService.getAll()
  meses.value = res.data
  if (meses.value.length > 0) {
    mesSeleccionado.value = meses.value[meses.value.length - 1].id
    await cargarTurnos()
  }
}

const cargarTurnos = async () => {
  if (!mesSeleccionado.value) return
  const res = await turnosService.get(mesSeleccionado.value)
  semanas.value = res.data.sort((a, b) => a.numero_semana - b.numero_semana)
}

const agregarSemana = async () => {
  if (!nuevosTurnos.value) return
  await turnosService.crear(
    mesSeleccionado.value,
    proximaSemana.value,
    nuevosTurnos.value,
    valorTurno.value
  )
  nuevosTurnos.value = ''
  await cargarTurnos()
}

const cambiarTurnos = async (semana, delta) => {
  const nuevoVal = Math.max(0, semana.turnos + delta)
  await turnosService.actualizar(semana.id, nuevoVal, semana.valor_turno)
  await cargarTurnos()
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
.metric-val.blue { color: #185FA5; }
.card { background: #fff; border: 1px solid #e5e5e3; border-radius: 12px; padding: 16px; }
.card-title { font-size: 11px; font-weight: 600; color: #888; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 14px; }
.semana-row { display: flex; align-items: center; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #f0f0ee; }
.semana-row:last-of-type { border-bottom: none; }
.semana-badge { background: #E6F1FB; color: #0C447C; font-size: 11px; font-weight: 600; padding: 4px 8px; border-radius: 6px; }
.semana-controls { display: flex; align-items: center; gap: 12px; }
.semana-turnos { font-size: 13px; color: #555; min-width: 60px; text-align: center; }
.semana-monto { font-size: 14px; font-weight: 600; min-width: 90px; text-align: right; }
.btn-round { width: 28px; height: 28px; border-radius: 50%; border: 1px solid #e5e5e3; background: #fff; cursor: pointer; font-size: 16px; display: flex; align-items: center; justify-content: center; }
.btn-round:hover { background: #f0f0ee; }
.semana-total { display: flex; justify-content: space-between; padding-top: 12px; margin-top: 8px; border-top: 1px solid #e5e5e3; font-size: 14px; font-weight: 600; }
.form-row { display: flex; gap: 12px; flex-wrap: wrap; }
.form-group { flex: 1; min-width: 120px; }
.form-group label { font-size: 12px; color: #888; display: block; margin-bottom: 4px; }
.input { width: 100%; padding: 8px 12px; border: 1px solid #e5e5e3; border-radius: 8px; font-size: 13px; }
.btn-primary { padding: 8px 16px; background: #185FA5; color: #fff; border: none; border-radius: 8px; font-size: 13px; cursor: pointer; white-space: nowrap; }
.btn-primary:hover { background: #0C447C; }
.breakdown-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f0f0ee; font-size: 13px; }
.breakdown-row:last-child { border-bottom: none; }
.breakdown-row.total { font-weight: 600; font-size: 14px; }
.lbl { color: #888; }
.neg { color: #993C1D; }
.blue { color: #185FA5; }
.semana-auto {
  padding: 8px 12px;
  background: var(--bg-metric);
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  color: #185FA5;
}

@media (max-width: 768px) {
  .metrics-row { grid-template-columns: 1fr 1fr; }
}
</style>
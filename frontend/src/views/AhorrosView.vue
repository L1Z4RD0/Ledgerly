<template>
  <div class="view">
    <div class="topbar">
      <div>
        <div class="topbar-title">Ahorros</div>
        <div class="topbar-sub">{{ ahorros.length }} ahorros registrados</div>
      </div>
      <div class="topbar-actions">
        <select v-model="mesSeleccionado" @change="cargarAportesMes" class="select-mes">
          <option v-for="m in meses" :key="m.id" :value="m.id">
            {{ nombreMes(m.mes) }} {{ m.anio }}
          </option>
        </select>
        <button @click="mostrarModal = true" class="btn-primary">+ Nuevo ahorro</button>
      </div>
    </div>

    <div class="page-content">
      <div class="metrics-row">
        <div class="metric-card">
          <div class="metric-label">Ahorros activos</div>
          <div class="metric-val">{{ ahorrosActivos.length }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Aportado este mes</div>
          <div class="metric-val green">{{ formatCLP(totalAportadoMes) }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Total a alcanzar</div>
          <div class="metric-val blue">{{ formatCLP(totalMeta) }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Total ahorrado histórico</div>
          <div class="metric-val green">{{ formatCLP(totalAhorradoHistorico) }}</div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Ahorros activos</div>
        <div v-if="ahorrosActivos.length === 0" class="empty-state">Sin ahorros activos</div>
        <div v-for="a in ahorrosActivos" :key="a.id" class="savings-item">
          <div class="savings-header">
            <div>
              <div class="savings-nombre">{{ a.nombre }}</div>
              <div class="savings-desc">{{ a.descripcion || 'Sin descripción' }}</div>
              <div class="savings-cuota">
                {{ a.tipo === 'fijo' ? 'Cuota: ' + formatCLP(a.cuota) + '/mes' : 'Cuota: ' + a.cuota + '% del sueldo' }}
              </div>
            </div>
            <div class="savings-right">
              <div class="savings-actions">
                <button @click="abrirAporte(a)" class="btn-aportar">Aportar</button>
                <button v-if="!a.monto_meta" @click="abrirRetiro(a)" class="btn-retirar">Retirar</button>
                <button @click="desactivar(a.id)" class="btn-delete">×</button>
              </div>
              <ProgressCircle v-if="a.monto_meta" :percentage="pctAhorrado(a)" type="ahorros" />
            </div>
          </div>
          <template v-if="a.monto_meta">
            <div class="savings-footer">
              <span>{{ formatCLP(a.monto_actual) }} ahorrado</span>
              <span>{{ formatCLP(a.monto_meta - a.monto_actual) }} para alcanzar meta</span>
            </div>
          </template>
          <template v-else>
            <div class="savings-footer">
              <span>{{ formatCLP(a.monto_actual) }} ahorrado</span>
              <span style="color: var(--text-secondary);">Sin meta definida</span>
            </div>
          </template>
        </div>
      </div>

      <div class="card" v-if="aportesMes.length > 0">
        <div class="card-title">Aportes registrados este mes</div>
        <div v-for="a in aportesMes" :key="a.id" class="aporte-row">
          <div class="aporte-info">
            <div class="aporte-nombre">{{ a.nombre_ahorro }}</div>
            <div class="aporte-fecha">{{ a.fecha }}</div>
          </div>
          <span class="aporte-monto">+{{ formatCLP(a.monto) }}</span>
        </div>
        <div class="aporte-total">
          <span>Total aportado este mes</span>
          <span class="green">+{{ formatCLP(totalAportadoMes) }}</span>
        </div>
      </div>

      <div class="card" v-if="ahorrosInactivos.length > 0">
        <div class="card-title">Ahorros completados</div>
        <div v-for="a in ahorrosInactivos" :key="a.id" class="savings-item">
          <div class="savings-header">
            <div>
              <div class="savings-nombre" style="color:var(--text-muted)">{{ a.nombre }}</div>
              <div class="savings-desc">{{ a.descripcion || 'Sin descripción' }}</div>
              <div class="savings-cuota">{{ formatCLP(a.monto_meta) }} — meta completada</div>
            </div>
            <span class="badge-ok">Completo</span>
            <ProgressCircle :percentage="100" type="ahorros" />
          </div>
        </div>
      </div>
    </div>

    <div v-if="mostrarModal" class="modal-overlay" @click.self="mostrarModal = false">
      <div class="modal">
        <div class="modal-title">Nuevo ahorro</div>
        <div class="form-group">
          <label>Nombre</label>
          <input v-model="nuevoNombre" type="text" class="input" placeholder="Ej: Consola, Laptop, Viaje, Ahorro general" />
        </div>
        <div class="form-group">
          <label>Descripción (opcional)</label>
          <input v-model="nuevoDesc" type="text" class="input" placeholder="Ej: Para mi cumpleaños" />
        </div>
        <div class="form-group">
          <div class="checkbox-group">
            <input v-model="tieneMetaOptional" type="checkbox" id="tieneMeta" />
            <label for="tieneMeta">¿Tiene meta?</label>
          </div>
        </div>
        <div v-if="tieneMetaOptional" class="form-group">
          <label>Meta (CLP)</label>
          <input v-model="nuevoMontoMeta" type="number" class="input" placeholder="Ej: 500000" />
        </div>
        <div class="form-group">
          <label>Tipo de aporte</label>
          <select v-model="nuevoTipo" class="input">
            <option value="fijo">Monto fijo mensual</option>
            <option value="porcentaje">Porcentaje del sueldo</option>
          </select>
        </div>
        <div class="form-group">
          <label>{{ nuevoTipo === 'fijo' ? 'Aporte sugerido (CLP)' : 'Porcentaje (%)' }}</label>
          <input v-model="nuevaCuota" type="number" class="input" :placeholder="nuevoTipo === 'fijo' ? 'Ej: 50000' : 'Ej: 5'" />
        </div>
        <div class="modal-actions">
          <button @click="mostrarModal = false" class="btn-secondary">Cancelar</button>
          <button @click="crearAhorro" class="btn-primary">Crear</button>
        </div>
      </div>
    </div>

    <div v-if="mostrarModalAporte" class="modal-overlay" @click.self="mostrarModalAporte = false">
      <div class="modal">
        <div class="modal-title">Registrar aporte — {{ ahorroSeleccionado?.nombre }}</div>
        <div v-if="ahorroSeleccionado?.tipo === 'porcentaje' && mesResumen" class="form-group info-box">
          <span class="info-label">Tipo:</span>
          <span class="info-value">{{ ahorroSeleccionado.cuota }}% del disponible</span>
          <span class="info-label" style="margin-top: 8px;">Disponible ahora:</span>
          <span class="info-value">{{ formatCLP(mesResumen.saldo_disponible || mesResumen.saldo_libre) }}</span>
          <span class="info-label" style="margin-top: 8px;">Monto a aportar:</span>
          <span class="info-value green">{{ formatCLP(montoCalculado) }}</span>
        </div>
        <div class="form-group">
          <label>Monto a aportar (CLP)</label>
          <input v-model.number="montoAporte" type="number" class="input" />
        </div>
        <div class="aviso" v-if="!mesSeleccionado">Selecciona un mes primero</div>
        <div class="aviso" v-if="excedeSaldoAporte">⚠️ No hay saldo disponible suficiente para este aporte. Disponible ahora: {{ formatCLP(disponibleActual) }}</div>
        <div class="modal-actions">
          <button @click="mostrarModalAporte = false" class="btn-secondary">Cancelar</button>
          <button @click="registrarAporte" class="btn-primary" :disabled="!mesSeleccionado || excedeSaldoAporte">Registrar</button>
        </div>
      </div>
    </div>

    <div v-if="mostrarModalRetiro" class="modal-overlay" @click.self="mostrarModalRetiro = false">
      <div class="modal">
        <div class="modal-title">Retirar dinero — {{ ahorroSeleccionado?.nombre }}</div>
        <div class="form-group info-box">
          <span class="info-label">Saldo actual:</span>
          <span class="info-value">{{ formatCLP(ahorroSeleccionado?.monto_actual) }}</span>
        </div>
        <div class="form-group">
          <label>Monto a retirar (CLP)</label>
          <input v-model.number="montoRetiro" type="number" class="input" placeholder="Monto a retirar" />
        </div>
        <div v-if="montoRetiro > ahorroSeleccionado?.monto_actual" class="aviso">
          ⚠️ El monto excede el saldo disponible
        </div>
        <div class="aviso" v-if="!mesSeleccionado">Selecciona un mes primero</div>
        <div class="modal-actions">
          <button @click="mostrarModalRetiro = false" class="btn-secondary">Cancelar</button>
          <button @click="registrarRetiro" class="btn-primary" :disabled="!mesSeleccionado || !montoRetiro">Retirar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { mesesService, ahorrosService } from '../services/api'
import ProgressCircle from '../components/ProgressCircle.vue'

const meses = ref([])
const mesSeleccionado = ref(null)
const ahorros = ref([])
const aportesMes = ref([])
const mesResumen = ref(null)
const mostrarModal = ref(false)
const mostrarModalAporte = ref(false)
const mostrarModalRetiro = ref(false)
const ahorroSeleccionado = ref(null)
const montoAporte = ref('')
const montoRetiro = ref('')
const montoCalculado = ref(0)
const nuevoNombre = ref('')
const nuevoDesc = ref('')
const nuevoMontoMeta = ref('')
const nuevoTipo = ref('fijo')
const nuevaCuota = ref('')
const tieneMetaOptional = ref(true)

const nombresMeses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
const nombreMes = (n) => nombresMeses[n - 1]
const formatCLP = (n) => '$' + Math.round(n || 0).toLocaleString('es-CL')
const pctAhorrado = (a) => a.monto_meta ? Math.min(100, Math.round((a.monto_actual / a.monto_meta) * 100)) : 0

const ahorrosActivos = computed(() => ahorros.value.filter(a => a.activo))
const ahorrosInactivos = computed(() => ahorros.value.filter(a => !a.activo))
const totalAportadoMes = computed(() => aportesMes.value.reduce((acc, a) => acc + a.monto, 0))
const totalMeta = computed(() => ahorrosActivos.value.filter(a => a.monto_meta).reduce((acc, a) => acc + a.monto_meta, 0))
const totalAhorradoHistorico = computed(() => ahorros.value.reduce((acc, a) => acc + a.monto_actual, 0))

const disponibleActual = computed(() => {
  if (!mesResumen.value) return 0
  return mesResumen.value.saldo_disponible !== null && mesResumen.value.saldo_disponible !== undefined
    ? mesResumen.value.saldo_disponible
    : (mesResumen.value.saldo_libre || 0)
})

const excedeSaldoAporte = computed(() => {
  const aporte = parseFloat(montoAporte.value) || 0
  return mesResumen.value && !mesResumen.value.mes_cerrado && aporte > disponibleActual.value
})

const cargarMeses = async () => {
  const res = await mesesService.getAll()
  meses.value = res.data
  if (meses.value.length > 0) {
    mesSeleccionado.value = meses.value[meses.value.length - 1].id
    await cargarAportesMes()
  }
}

const cargarAhorros = async () => {
  const res = await ahorrosService.getAll()
  ahorros.value = res.data
}

const cargarAportesMes = async () => {
  if (!mesSeleccionado.value) return
  const res = await ahorrosService.getAportesMes(mesSeleccionado.value)
  aportesMes.value = res.data
  await cargarResumenMes()
}

const cargarResumenMes = async () => {
  if (!mesSeleccionado.value) return
  try {
    const res = await mesesService.getResumen(mesSeleccionado.value)
    mesResumen.value = res.data
  } catch {
    mesResumen.value = null
  }
}

const calcularMontoAporte = (ahorro) => {
  if (ahorro.tipo === 'fijo') {
    return ahorro.cuota
  } else if (ahorro.tipo === 'porcentaje' && mesResumen.value) {
    const disponible = mesResumen.value.saldo_disponible || mesResumen.value.saldo_libre || 0
    return (ahorro.cuota / 100) * disponible
  }
  return ahorro.cuota
}

const crearAhorro = async () => {
  if (!nuevoNombre.value || !nuevaCuota.value) return
  const meta = tieneMetaOptional.value && nuevoMontoMeta.value ? parseFloat(nuevoMontoMeta.value) : null
  await ahorrosService.crear(nuevoNombre.value, nuevoDesc.value, meta, nuevaCuota.value, nuevoTipo.value)
  nuevoNombre.value = ''
  nuevoDesc.value = ''
  nuevoMontoMeta.value = ''
  nuevaCuota.value = ''
  tieneMetaOptional.value = true
  mostrarModal.value = false
  await cargarAhorros()
}

const abrirAporte = (a) => {
  ahorroSeleccionado.value = a
  montoCalculado.value = calcularMontoAporte(a)
  montoAporte.value = montoCalculado.value
  mostrarModalAporte.value = true
}

const abrirRetiro = (a) => {
  ahorroSeleccionado.value = a
  montoRetiro.value = ''
  mostrarModalRetiro.value = true
}

const registrarAporte = async () => {
  if (!montoAporte.value || !mesSeleccionado.value) return

  if (excedeSaldoAporte.value) {
    alert(`Saldo insuficiente. Disponible: ${formatCLP(disponibleActual.value)}`)
    return
  }

  try {
    await ahorrosService.aportar(ahorroSeleccionado.value.id, mesSeleccionado.value, parseFloat(montoAporte.value))
    mostrarModalAporte.value = false
    montoAporte.value = ''
    await cargarAhorros()
    await cargarAportesMes()
  } catch (error) {
    const detalle = error.response?.data?.detail || 'No se pudo registrar el aporte.'
    alert(detalle)
  }
}

const registrarRetiro = async () => {
  if (!montoRetiro.value || !mesSeleccionado.value) return
  const montoNegativo = -parseFloat(montoRetiro.value)
  await ahorrosService.aportar(ahorroSeleccionado.value.id, mesSeleccionado.value, montoNegativo)
  mostrarModalRetiro.value = false
  montoRetiro.value = ''
  await cargarAhorros()
  await cargarAportesMes()
}

const desactivar = async (id) => {
  await ahorrosService.desactivar(id)
  await cargarAhorros()
}

onMounted(async () => {
  await cargarAhorros()
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
.metric-val.green { color: #0F6E56; }
.metric-val.blue { color: #185FA5; }
.card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 16px; }
.card-title { font-size: 11px; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 14px; }
.savings-item { padding: 12px 0; border-bottom: 1px solid var(--border-light); }
.savings-item:last-child { border-bottom: none; }
.savings-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; }
.savings-nombre { font-size: 14px; font-weight: 600; color: var(--text-primary); }
.savings-desc { font-size: 12px; color: var(--text-secondary); margin-top: 2px; }
.savings-cuota { font-size: 12px; color: var(--text-secondary); margin-top: 2px; }
.savings-right { display: flex; gap: 12px; align-items: center; }
.savings-actions { display: flex; gap: 8px; align-items: center; }
.btn-aportar { padding: 6px 12px; background: #E6F1FB; color: #185FA5; border: none; border-radius: 6px; font-size: 12px; cursor: pointer; font-weight: 500; }
.btn-aportar:hover { background: #B5D4F4; }
.btn-delete { background: none; border: none; color: var(--text-muted); font-size: 20px; cursor: pointer; }
.btn-delete:hover { color: #993C1D; }
.progress-bar { background: var(--bg-metric); border-radius: 4px; height: 6px; overflow: hidden; margin-bottom: 6px; }
.progress-fill { height: 100%; border-radius: 4px; background: #0F6E56; transition: width 0.3s; }
.savings-footer { display: flex; justify-content: space-between; font-size: 11px; color: var(--text-muted); }
.aporte-row { display: flex; align-items: center; justify-content: space-between; padding: 9px 0; border-bottom: 1px solid var(--border-light); }
.aporte-row:last-of-type { border-bottom: none; }
.aporte-info .aporte-nombre { font-size: 13px; font-weight: 500; color: var(--text-primary); }
.aporte-info .aporte-fecha { font-size: 11px; color: var(--text-muted); margin-top: 2px; }
.aporte-monto { font-size: 14px; font-weight: 600; color: #0F6E56; }
.aporte-total { display: flex; justify-content: space-between; padding-top: 12px; margin-top: 8px; border-top: 1px solid var(--border); font-size: 14px; font-weight: 600; }
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
.green { color: #0F6E56; }
.info-box { background: var(--bg-metric); border-radius: 8px; padding: 12px; display: flex; flex-direction: column; gap: 8px; }
.info-label { font-size: 11px; color: var(--text-secondary); font-weight: 500; text-transform: uppercase; }
.info-value { font-size: 14px; font-weight: 600; color: var(--text-primary); }
.btn-retirar { padding: 6px 12px; background: #FFE6CC; color: #B35900; border: none; border-radius: 6px; font-size: 12px; cursor: pointer; font-weight: 500; }
.btn-retirar:hover { background: #FFCFA3; }
.checkbox-group { display: flex; align-items: center; gap: 8px; }
.checkbox-group input { width: 16px; height: 16px; cursor: pointer; }
.checkbox-group label { font-size: 12px; color: var(--text-primary); cursor: pointer; margin: 0; }

@media (max-width: 768px) {
  .metrics-row { grid-template-columns: 1fr 1fr; }
}
</style>

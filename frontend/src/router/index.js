import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import TurnosView from '../views/TurnosView.vue'
import GastosView from '../views/GastosView.vue'
import DeudasView from '../views/DeudasView.vue'
import AhorrosView from '../views/AhorrosView.vue'
import ExtrasView from '../views/ExtrasView.vue'
import StatsView from '../views/StatsView.vue'
import HistorialView from '../views/HistorialView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', component: HomeView },
    { path: '/turnos', component: TurnosView },
    { path: '/gastos', component: GastosView },
    { path: '/deudas', component: DeudasView },
    { path: '/ahorros', component: AhorrosView },
    { path: '/extras', component: ExtrasView },
    { path: '/stats', component: StatsView },
    { path: '/historial', component: HistorialView }
  ]
})

export default router
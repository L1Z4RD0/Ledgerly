<template>
  <div class="app-layout" :class="{ dark: isDark }">
    <!-- Sidebar para desktop y drawer para mobile -->
    <aside class="sidebar" :class="{ 'mobile-drawer-open': menuOpen && isMobile }">
      <div class="sidebar-header">
        <span class="logo">Ledgerly</span>
        <span class="logo-sub">{{ mesActual }}</span>
      </div>
      <nav>
        <span class="nav-section">General</span>
        <RouterLink to="/" class="nav-item" @click="cerrarMenu">
          <span class="nav-icon">◈</span> Inicio
        </RouterLink>
        <RouterLink to="/turnos" class="nav-item" @click="cerrarMenu">
          <span class="nav-icon">◷</span> Turnos
        </RouterLink>
        <RouterLink to="/gastos" class="nav-item" @click="cerrarMenu">
          <span class="nav-icon">◉</span> Gastos
        </RouterLink>
        <RouterLink to="/deudas" class="nav-item" @click="cerrarMenu">
          <span class="nav-icon">◎</span> Deudas
        </RouterLink>
        <RouterLink to="/ahorros" class="nav-item" @click="cerrarMenu">
          <span class="nav-icon">◆</span> Ahorros
        </RouterLink>
        <RouterLink to="/extras" class="nav-item" @click="cerrarMenu">
          <span class="nav-icon">+</span> Extras
        </RouterLink>
        <span class="nav-section">Análisis</span>
        <RouterLink to="/stats" class="nav-item" @click="cerrarMenu">
          <span class="nav-icon">▦</span> Estadísticas
        </RouterLink>
        <RouterLink to="/historial" class="nav-item" @click="cerrarMenu">
          <span class="nav-icon">◁</span> Historial
        </RouterLink>
      </nav>
      <div class="sidebar-footer">
        <div class="footer-top">
          <span class="footer-label">Valor turno</span>
          <span class="footer-val">$16.000 CLP</span>
        </div>
        <div class="theme-toggle" @click="toggleDark">
          <span class="theme-icon">{{ isDark ? '☀' : '☾' }}</span>
          <span class="theme-label">{{ isDark ? 'Modo claro' : 'Modo oscuro' }}</span>
          <div class="switch" :class="{ on: isDark }">
            <div class="switch-thumb"></div>
          </div>
        </div>
      </div>
    </aside>

    <!-- Overlay para cerrar el menú en mobile -->
    <div v-if="menuOpen && isMobile" class="mobile-overlay" @click="menuOpen = false"></div>

    <!-- Botón hamburguesa para mobile -->
    <div v-if="isMobile" class="mobile-header">
      <button class="hamburger" @click="menuOpen = !menuOpen" :class="{ active: menuOpen }">
        <span></span>
        <span></span>
        <span></span>
      </button>
      <span class="mobile-title">Ledgerly</span>
    </div>

    <main class="main-content" :class="{ 'main-mobile': isMobile }">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { RouterLink, RouterView } from 'vue-router'

const windowWidth = ref(window.innerWidth)
const menuOpen = ref(false)
const isMobile = computed(() => windowWidth.value < 768)
const isDark = ref(localStorage.getItem('ledgerly-theme') === 'dark')

const mesActual = computed(() => {
  const now = new Date()
  return now.toLocaleString('es-CL', { month: 'long', year: 'numeric' })
})

const toggleDark = () => {
  isDark.value = !isDark.value
  localStorage.setItem('ledgerly-theme', isDark.value ? 'dark' : 'light')
}

const cerrarMenu = () => {
  menuOpen.value = false
}

const handleResize = () => { 
  windowWidth.value = window.innerWidth
  if (windowWidth.value >= 768) {
    menuOpen.value = false
  }
}

onMounted(() => window.addEventListener('resize', handleResize))
onUnmounted(() => window.removeEventListener('resize', handleResize))
</script>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }

/* ── Modo claro ── */
.app-layout {
  display: flex;
  min-height: 100vh;
  font-family: system-ui, sans-serif;
  background: #f5f5f3;
  color: #1a1a1a;
  --bg: #f5f5f3;
  --bg-card: #ffffff;
  --bg-metric: #efefed;
  --bg-sidebar: #ffffff;
  --border: #e5e5e3;
  --border-light: #f0f0ee;
  --text-primary: #1a1a1a;
  --text-secondary: #888888;
  --text-muted: #aaaaaa;
  --nav-active-bg: #e8f0fb;
  --nav-active-color: #185FA5;
  --nav-hover: #f5f5f3;
  --accent: #185FA5;
  --accent-dark: #0C447C;
  --switch-off: #d0d0ce;
}

/* ── Modo oscuro ── */
.app-layout.dark {
  background: #1a1a1a;
  color: #e8e8e6;
  --bg: #1a1a1a;
  --bg-card: #242424;
  --bg-metric: #2a2a2a;
  --bg-sidebar: #1e1e1e;
  --border: #333333;
  --border-light: #2e2e2e;
  --text-primary: #e8e8e6;
  --text-secondary: #999999;
  --text-muted: #666666;
  --nav-active-bg: #1a2d45;
  --nav-active-color: #5BA3E0;
  --nav-hover: #2a2a2a;
  --accent: #5BA3E0;
  --accent-dark: #378ADD;
  --switch-off: #444444;
}

body { margin: 0; }

.sidebar {
  width: 210px;
  flex-shrink: 0;
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0; left: 0;
  height: 100vh;
  z-index: 100;
  transition: background 0.2s, border-color 0.2s;
}

@media (max-width: 767px) {
  .sidebar {
    position: fixed;
    top: 0;
    left: -210px;
    width: 210px;
    height: 100vh;
    z-index: 101;
    transition: left 0.3s ease;
  }
  .sidebar.mobile-drawer-open {
    left: 0;
  }
}

.sidebar-header {
  padding: 20px 16px 16px;
  border-bottom: 1px solid var(--border);
}
.logo { font-size: 16px; font-weight: 600; color: var(--text-primary); display: block; }
.logo-sub { font-size: 11px; color: var(--text-secondary); margin-top: 2px; display: block; text-transform: capitalize; }

nav { flex: 1; padding: 8px 0; }
.nav-section { font-size: 10px; color: var(--text-muted); padding: 12px 16px 4px; display: block; text-transform: uppercase; letter-spacing: 0.5px; }
.nav-item { display: flex; align-items: center; gap: 10px; padding: 9px 16px; font-size: 13px; color: var(--text-secondary); text-decoration: none; transition: all 0.15s; }
.nav-item:hover { background: var(--nav-hover); color: var(--text-primary); }
.nav-item.router-link-active { background: var(--nav-active-bg); color: var(--nav-active-color); font-weight: 500; border-right: 2px solid var(--nav-active-color); }
.nav-icon { font-size: 14px; width: 16px; text-align: center; }

.sidebar-footer {
  padding: 14px 16px;
  border-top: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.footer-label { font-size: 11px; color: var(--text-muted); display: block; }
.footer-val { font-size: 14px; font-weight: 500; color: var(--text-primary); display: block; margin-top: 2px; }

.theme-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 10px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--bg-metric);
  transition: all 0.15s;
}
.theme-toggle:hover { border-color: var(--accent); }
.theme-icon { font-size: 14px; }
.theme-label { font-size: 12px; color: var(--text-secondary); flex: 1; }

.switch {
  width: 32px;
  height: 18px;
  border-radius: 9px;
  background: var(--switch-off);
  position: relative;
  transition: background 0.2s;
  flex-shrink: 0;
}
.switch.on { background: var(--accent); }
.switch-thumb {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: white;
  position: absolute;
  top: 3px;
  left: 3px;
  transition: left 0.2s;
}
.switch.on .switch-thumb { left: 17px; }

.main-content { margin-left: 210px; flex: 1; min-height: 100vh; transition: background 0.2s; }

@media (max-width: 767px) {
  .main-content {
    margin-left: 0;
    margin-top: 50px;
  }
}

.main-mobile { margin-left: 0; margin-top: 50px; }

.mobile-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 99;
}

.mobile-header {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 50px;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border);
  z-index: 98;
  align-items: center;
  gap: 12px;
  padding: 0 16px;
}

@media (max-width: 767px) {
  .mobile-header {
    display: flex;
  }
}

.hamburger {
  width: 32px;
  height: 32px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 5px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  flex-shrink: 0;
}

.hamburger span {
  width: 22px;
  height: 2px;
  background: var(--text-primary);
  border-radius: 1px;
  transition: all 0.3s ease;
}

.hamburger.active span:nth-child(1) {
  transform: rotate(45deg) translate(8px, 8px);
}

.hamburger.active span:nth-child(2) {
  opacity: 0;
}

.hamburger.active span:nth-child(3) {
  transform: rotate(-45deg) translate(7px, -7px);
}

.mobile-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  flex: 1;
}

.mobile-tabs {
  display: none;
}
</style>
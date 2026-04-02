<template>
  <div class="progress-circle-wrapper">
    <svg class="progress-circle-svg" viewBox="0 0 100 100">
      <!-- Círculo de fondo -->
      <circle cx="50" cy="50" r="45" class="progress-circle-bg"></circle>
      <!-- Círculo de progreso -->
      <circle 
        cx="50" 
        cy="50" 
        r="45" 
        class="progress-circle-fill"
        :class="colorClass"
        :style="{ strokeDashoffset: strokeDashoffset }"
      ></circle>
    </svg>
    <div class="progress-circle-text">{{ percentage }}%</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  percentage: {
    type: Number,
    required: true
  },
  type: {
    type: String,
    default: 'deudas',
    validator: (value) => ['deudas', 'ahorros'].includes(value)
  }
})

const circumference = 2 * Math.PI * 45
const strokeDashoffset = computed(() => {
  const progress = Math.min(100, Math.max(0, props.percentage))
  return circumference - (progress / 100) * circumference
})

const colorClass = computed(() => `color-${props.type}`)
</script>

<style scoped>
.progress-circle-wrapper {
  position: relative;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.progress-circle-svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.progress-circle-bg {
  fill: none;
  stroke: var(--bg-metric);
  stroke-width: 4;
}

.progress-circle-fill {
  fill: none;
  stroke-width: 4;
  stroke-dasharray: v-bind(circumference);
  stroke-linecap: round;
  transition: stroke-dashoffset 0.3s ease;
}

.progress-circle-fill.color-deudas {
  stroke: #185FA5;
}

.progress-circle-fill.color-ahorros {
  stroke: #0F6E56;
}

.progress-circle-text {
  position: absolute;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  pointer-events: none;
}
</style>


<template>
  <span class="help-tip" tabindex="0">
    <span class="help-button" aria-label="Información del gráfico">?</span>
    <span class="help-popup" role="tooltip">{{ props.message }}</span>
  </span>
</template>

<script setup>
const props = defineProps({
  message: {
    type: String,
    required: true
  }
})
</script>

<style scoped>
.help-tip {
  display: inline-flex;
  align-items: center;
  position: relative;
  margin-left: 8px;
  cursor: pointer;
}

.help-button {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #e2e8f0;
  color: #1f2937;
  font-size: 12px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #cbd5e1;
}

.help-popup {
  position: absolute;
  bottom: 125%;
  left: 50%;
  transform: translateX(-50%);
  min-width: 180px;
  max-width: 240px;
  background: rgba(15, 23, 42, 0.95);
  color: #f8fafc;
  font-size: 12px;
  line-height: 1.4;
  border-radius: 10px;
  padding: 10px;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.15s ease, transform 0.15s ease;
  z-index: 10;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.18);
}

.help-tip:hover .help-popup,
.help-tip:focus-within .help-popup {
  opacity: 1;
  transform: translateX(-50%) translateY(-4px);
  pointer-events: auto;
}

.help-popup::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border-width: 6px;
  border-style: solid;
  border-color: rgba(15, 23, 42, 0.95) transparent transparent transparent;
}
</style>

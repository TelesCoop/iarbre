<script lang="ts" setup>
interface SpinnerProps {
  size?: "sm" | "md" | "lg"
  strokeWidth?: number
  color?: string
}

const props = withDefaults(defineProps<SpinnerProps>(), {
  size: "md",
  strokeWidth: 4,
  color: "currentColor"
})

const sizeMap = {
  sm: 24,
  md: 50,
  lg: 80
}

const spinnerSize = sizeMap[props.size]
</script>

<template>
  <div class="app-spinner" role="status" aria-label="Chargement en cours">
    <svg :width="spinnerSize" :height="spinnerSize" viewBox="0 0 50 50" class="animate-spin">
      <circle
        cx="25"
        cy="25"
        r="20"
        fill="none"
        :stroke="color"
        :stroke-width="strokeWidth"
        stroke-linecap="round"
        class="spinner-circle"
      />
    </svg>
  </div>
</template>

<style scoped>
.app-spinner {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.spinner-circle {
  stroke-dasharray: 90, 150;
  stroke-dashoffset: 0;
  animation: spinner-dash 1.5s ease-in-out infinite;
}

@keyframes spinner-dash {
  0% {
    stroke-dasharray: 1, 150;
    stroke-dashoffset: 0;
  }
  50% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -35;
  }
  100% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -124;
  }
}
</style>

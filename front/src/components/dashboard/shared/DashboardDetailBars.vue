<script lang="ts" setup>
interface DetailItem {
  label: string
  value: number
  color: string
}

interface Props {
  items: DetailItem[]
  unit?: string
}

withDefaults(defineProps<Props>(), {
  unit: "%"
})
</script>

<template>
  <div class="detail-bars">
    <div v-for="item in items" :key="item.label" class="detail-item">
      <div class="detail-label-row">
        <span :style="{ backgroundColor: item.color }" class="detail-dot" />
        <span class="detail-label">{{ item.label }}</span>
        <span class="detail-value">{{ item.value.toFixed(1) }}{{ unit }}</span>
      </div>
      <div class="bar-track">
        <div :style="{ width: `${item.value}%`, backgroundColor: item.color }" class="bar-fill" />
      </div>
    </div>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.detail-bars {
  @apply flex flex-col gap-2.5;
}

.detail-item {
  @apply flex flex-col gap-1;
}

.detail-label-row {
  @apply flex items-center gap-2 text-xs;
}

.detail-dot {
  @apply w-2 h-2 rounded-full shrink-0;
}

.detail-label {
  @apply text-gray-500;
}

.detail-value {
  @apply font-semibold text-gray-700 ml-auto tabular-nums;
}

.bar-track {
  @apply w-full h-1.5 bg-gray-100 rounded-full overflow-hidden;
}

.bar-fill {
  @apply h-full rounded-full;
  animation: barGrow 700ms ease-out both;
}

@keyframes barGrow {
  from {
    width: 0 !important;
  }
}
</style>

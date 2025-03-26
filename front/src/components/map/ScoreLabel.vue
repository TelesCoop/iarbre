<script setup lang="ts">
import { computed } from "vue"

const props = defineProps({
  score: {
    required: true,
    type: Number
  },
  label: {
    required: true,
    type: String
  },
  size: {
    required: true,
    type: String
  }
})

const scoreBg: Record<number, string> = {
  0: "bg-scale-0",
  1: "bg-scale-1",
  2: "bg-scale-2",
  3: "bg-scale-3",
  4: "bg-scale-4",
  5: "bg-scale-5",
  6: "bg-scale-6",
  7: "bg-scale-7",
  8: "bg-scale-8",
  9: "bg-scale-9",
  10: "bg-scale-10"
}

const backgroundClass = computed(() => scoreBg[props.score])
const sizeClass = computed(() => props.size)
</script>

<template>
  <div class="hexagon relative m-[5px] block text-center" :class="[backgroundClass, sizeClass]">
    <span>{{ label }}</span>
  </div>
</template>

<style scoped>
.hexagon {
  position: relative;
}

.hexagon::before,
.hexagon::after {
  content: "";
  position: absolute;
  width: 0;
  left: 0;
}

.hexagon::before {
  bottom: 100%;
}

.hexagon::after {
  top: 100%;
}

/* Small hexagon */
.hexagon.small {
  height: calc(1.732 * 12px); /* sqrt(3) * 12px */
  width: calc(3 * 12px);
  margin-top: calc(12px + 5px);
  margin-bottom: calc(12px + 5px);
  font-size: 1.3rem;
}

.hexagon.small::before {
  border-left: calc(1.5 * 12px) solid transparent;
  border-right: calc(1.5 * 12px) solid transparent;
  border-bottom: calc(1.732 / 2 * 12px) solid transparent;
}

.hexagon.small::after {
  border-left: calc(1.5 * 12px) solid transparent;
  border-right: calc(1.5 * 12px) solid transparent;
  border-top: calc(1.732 / 2 * 12px) solid transparent;
}

/* Huge hexagon */
.hexagon.huge {
  height: calc(1.732 * 20px); /* sqrt(3) * 20px */
  width: calc(3 * 20px);
  margin-top: calc(20px + 5px);
  margin-bottom: calc(20px + 5px);
  font-size: 1.2rem;
  line-height: 2.3rem;
}

.hexagon.huge::before {
  border-left: calc(1.5 * 20px) solid transparent;
  border-right: calc(1.5 * 20px) solid transparent;
  border-bottom: calc(1.732 / 2 * 20px) solid transparent;
}

.hexagon.huge::after {
  border-left: calc(1.5 * 20px) solid transparent;
  border-right: calc(1.5 * 20px) solid transparent;
  border-top: calc(1.732 / 2 * 20px) solid transparent;
}
</style>

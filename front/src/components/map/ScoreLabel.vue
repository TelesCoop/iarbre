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
  0: "bg-scale-0 border-scale-0",
  1: "bg-scale-1 border-scale-1",
  2: "bg-scale-2 border-scale-2",
  3: "bg-scale-3 border-scale-3",
  4: "bg-scale-4 border-scale-4",
  5: "bg-scale-5 border-scale-5",
  6: "bg-scale-6 border-scale-6",
  7: "bg-scale-7 border-scale-7",
  8: "bg-scale-8 border-scale-8",
  9: "bg-scale-9 border-scale-9",
  10: "bg-scale-10 border-scale-10 text-white"
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
  display: flex;
  justify-content: center;
  align-items: center;
  clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
}
.hexagon.small {
  height: 2em;
  width: 2em;
  font-size: 1.5em;
}
.hexagon.huge {
  height: 4em;
  width: 4em;
  font-size: 1.5em;
}
</style>

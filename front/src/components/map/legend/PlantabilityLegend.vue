<script lang="ts" setup></script>

<template>
  <div
    class="font-accent flex items-center justify-center text-xs leading-3 gap-2"
    data-cy="plantability-legend"
  >
    <div class="flex items-center flex-wrap justify-center gap-[7px] px-2">
      <span class="text-sm leading-3">Non plantable</span>
      <score-label
        v-for="index in [0, 2, 4, 6, 8, 10]"
        :key="index"
        :label="`${index}`"
        :score="index"
        class="flex items-center justify-center"
      />
    </div>
    <span class="text-sm leading-3">Plantable</span>
  </div>
</template>

<script lang="ts" setup>
import { PLANTABILITY_COLOR_MAP } from "@/utils/plantability"
</script>
<template>
  <svg viewBox="0 0 30 20" width="45">
    <rect x="0" y="7" width="5" height="35" :fill="PLANTABILITY_COLOR_MAP[1] as string" />
    <rect x="5" y="7" width="5" height="35" :fill="PLANTABILITY_COLOR_MAP[5] as string" />
    <rect x="10" y="7" width="5" height="35" :fill="PLANTABILITY_COLOR_MAP[9] as string" />
    <rect x="15" y="7" width="5" height="35" :fill="PLANTABILITY_COLOR_MAP[13] as string" />
    <rect x="20" y="7" width="5" height="35" :fill="PLANTABILITY_COLOR_MAP[17] as string" />
    <rect x="25" y="7" width="5" height="35" :fill="PLANTABILITY_COLOR_MAP[21] as string" />
  </svg>
</template>

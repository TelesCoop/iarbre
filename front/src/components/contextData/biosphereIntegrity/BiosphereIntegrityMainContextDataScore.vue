<script lang="ts" setup>
import type { BiosphereIntegrityData } from "@/types/biosphereIntegrity"

interface BiosphereIntegrityMainScoreProps {
  data: BiosphereIntegrityData
}

defineProps<BiosphereIntegrityMainScoreProps>()
</script>
<template>
  <CircularScore
    :score="data.indice / 100"
    :max-score="1"
    :percentage="data.indice"
    name="IFB"
    label="ifb"
    color-scheme="biosphereIntegrity"
  />
</template>

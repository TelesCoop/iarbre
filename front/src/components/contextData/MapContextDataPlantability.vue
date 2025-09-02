<script lang="ts" setup>
import { computed, withDefaults } from "vue"
import { type PlantabilityData } from "@/types/plantability"
import MapContextHeader from "@/components/contextData/MapContextHeader.vue"
import PlantabilityContextDataScore from "@/components/contextData/plantability/PlantabilityContextDataScore.vue"
import PlantabilityContextDataList from "@/components/contextData/plantability/PlantabilityContextDataList.vue"
import { DataType, DataTypeToLabel } from "@/utils/enum"

interface PlantabilityCardProps {
  data?: PlantabilityData | null
  hideCloseButton?: boolean
}

const props = withDefaults(defineProps<PlantabilityCardProps>(), {
  data: null,
  hideCloseButton: false
})

const emit = defineEmits<{
  close: []
}>()

const scorePercentage = computed(() =>
  props.data?.plantabilityNormalizedIndice !== undefined
    ? props.data.plantabilityNormalizedIndice * 10
    : null
)
</script>

<template>
  <div
    aria-describedby="plantability-description"
    aria-labelledby="plantability-title"
    class="map-context-panel item-center"
    role="dialog"
  >
    <map-context-header
      description="Calcul basé sur la pondération de +37 paramètres"
      :title="DataTypeToLabel[DataType.PLANTABILITY]"
      :hide-close-button="props.hideCloseButton"
      @close="emit('close')"
    />
    <div class="map-context-panel-content">
      <plantability-context-data-score
        v-if="props.data && scorePercentage !== null"
        :percentage="scorePercentage"
        :score="props.data.plantabilityNormalizedIndice"
      />
      <empty-message v-else data-cy="empty-message" message="Zommez et cliquez sur un carreau" />
      <plantability-context-data-list v-if="props.data" :data="props.data" />
    </div>
  </div>
</template>

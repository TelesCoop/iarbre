<script lang="ts" setup>
import { computed } from "vue"
import type { City } from "@/types/division"
import IpaveDivisionDataDisplay from "./IpaveDivisionDataDisplay.vue"
import { Card } from "primevue"

interface IpaveDivisionDataProps {
  city?: City | null
}

const props = withDefaults(defineProps<IpaveDivisionDataProps>(), {
  city: null
})

const hasCity = computed(() => props.city !== null && props.city !== undefined)
</script>

<template>
  <Card
    class="w-full bg-white rounded-lg border-1 border-gray-200 mt-6"
    :pt="{ body: { class: 'p-4!' } }"
  >
    <template #header>
      <h3 class="text-md text-center font-semibold text-gray-700 pt-4">
        Données de végétation de voirie
      </h3>
    </template>
    <template #content>
      <div v-if="hasCity && props.city">
        <h4 class="text-sm font-semibold text-gray-600 mb-3">Commune</h4>
        <IpaveDivisionDataDisplay :data="props.city" />
      </div>
      <div v-else class="p-4 text-center text-gray-500">Aucune donnée de commune disponible</div>
    </template>
  </Card>
</template>

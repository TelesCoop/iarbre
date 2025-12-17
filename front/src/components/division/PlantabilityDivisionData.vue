<script lang="ts" setup>
import { computed } from "vue"
import type { City, Iris } from "@/types/division"
import DivisionDataDisplay from "./DivisionDataDisplay.vue"
import { Accordion, AccordionPanel, AccordionHeader, AccordionContent, Card } from "primevue"

interface DivisionDataProps {
  cities?: City[]
  irisList?: Iris[]
}

const props = withDefaults(defineProps<DivisionDataProps>(), {
  cities: () => [],
  irisList: () => []
})

const hasCities = computed(() => props.cities && props.cities.length > 0)
const hasIris = computed(() => props.irisList && props.irisList.length > 0)
</script>

<template>
  <Card
    class="w-full bg-white rounded-lg border-1 border-gray-200 mt-6"
    :pt="{ body: { class: 'p-4!' } }"
  >
    <template #header>
      <h3 class="text-md text-center font-semibold text-gray-700 pt-4">
        Données aux échelons supérieurs
      </h3>
    </template>
    <template #content>
      <!-- Communes Section -->
      <div v-if="hasCities" class="mb-6">
        <h4 class="text-sm font-semibold text-gray-700 mb-3">Communes</h4>
        <Accordion multiple>
          <AccordionPanel
            v-for="(city, index) in props.cities"
            :key="`city-${city.id}`"
            :value="`city-${index}`"
          >
            <AccordionHeader>{{ city.name || city.code }}</AccordionHeader>
            <AccordionContent>
              <DivisionDataDisplay :data="city" />
            </AccordionContent>
          </AccordionPanel>
        </Accordion>
      </div>

      <!-- IRIS Section -->
      <div v-if="hasIris">
        <h4 class="text-sm font-semibold text-gray-700 mb-3">IRIS</h4>
        <Accordion multiple>
          <AccordionPanel
            v-for="(iris, index) in props.irisList"
            :key="`iris-${iris.id}`"
            :value="`iris-${index}`"
          >
            <AccordionHeader>{{ iris.name || iris.code }}</AccordionHeader>
            <AccordionContent>
              <DivisionDataDisplay :data="iris" />
            </AccordionContent>
          </AccordionPanel>
        </Accordion>
      </div>

      <!-- Empty State -->
      <div v-if="!hasCities && !hasIris" class="p-4 text-center text-gray-500">
        Aucune donnée disponible
      </div>
    </template>
  </Card>
</template>

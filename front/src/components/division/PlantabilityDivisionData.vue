<script lang="ts" setup>
import { computed } from "vue"
import type { City, Iris } from "@/types/division"
import DivisionDataDisplay from "./DivisionDataDisplay.vue"
import { Accordion, AccordionPanel, AccordionHeader, AccordionContent, Card } from "primevue"

interface DivisionDataProps {
  city?: City | null
  iris?: Iris | null
}

const props = withDefaults(defineProps<DivisionDataProps>(), {
  city: null,
  iris: null
})

const hasCity = computed(() => props.city !== null && props.city !== undefined)
const hasIris = computed(() => props.iris !== null && props.iris !== undefined)
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
      <Accordion multiple>
        <AccordionPanel value="0" :disabled="!hasCity">
          <AccordionHeader>Commune</AccordionHeader>
          <AccordionContent>
            <DivisionDataDisplay v-if="props.city" :data="props.city" />
            <div v-else class="p-4 text-center text-gray-500">
              Aucune donnée de commune disponible
            </div>
          </AccordionContent>
        </AccordionPanel>

        <AccordionPanel value="1" :disabled="!hasIris">
          <AccordionHeader>IRIS</AccordionHeader>
          <AccordionContent>
            <DivisionDataDisplay v-if="props.iris" :data="props.iris" />
            <div v-else class="p-4 text-center text-gray-500">Aucune donnée IRIS disponible</div>
          </AccordionContent>
        </AccordionPanel>
      </Accordion>
    </template>
  </Card>
</template>

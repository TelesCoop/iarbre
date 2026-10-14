<script lang="ts" setup>
import { DataType, DataTypeToDocumentationUrl } from "@/utils/enum"
import IconUndergroundParking from "@/components/icons/IconUndergroundParking.vue"
import IconCrosswalk from "@/components/icons/IconCrosswalk.vue"
import IconStreetFurniture from "@/components/icons/IconStreetFurniture.vue"
import IconUpcomingProjects from "@/components/icons/IconUpcomingProjects.vue"
import IconWarning from "@/components/icons/IconWarning.vue"
import IconArrowRight from "@/components/icons/IconArrowRight.vue"

const documentationUrl = DataTypeToDocumentationUrl[DataType.PLANTABILITY]

const limits = [
  { label: "Parkings souterrains", icon: IconUndergroundParking },
  { label: "Passages piétons", icon: IconCrosswalk },
  { label: "Mobilier urbain", icon: IconStreetFurniture },
  { label: "Projets à venir", icon: IconUpcomingProjects }
]
</script>

<template>
  <section class="flex flex-col gap-3 w-full text-left" data-cy="plantability-limits">
    <p class="text-sm text-brown">
      Certaines <b>contraintes n'apparaissent pas dans les données</b> ou les données ne sont pas
      encore à jour.
    </p>
    <ul class="grid grid-cols-4 gap-2">
      <li
        v-for="limit in limits"
        :key="limit.label"
        class="flex flex-col items-center gap-1 text-center text-xs text-gray-500"
      >
        <component :is="limit.icon" :size="24" class="text-brown" aria-hidden="true" />
        <span>{{ limit.label }}</span>
      </li>
    </ul>
    <p class="flex items-center gap-2 rounded-md bg-gold-50 px-3 py-2 text-sm text-brown">
      <IconWarning :size="16" class="shrink-0" aria-hidden="true" />
      Domaine privé : nous disposons de moins de données, le calque est donc souvent optimiste.
    </p>
    <div
      class="flex flex-wrap items-center justify-between gap-2 border-t border-gray-200 pt-3 text-sm"
    >
      <a
        :href="documentationUrl"
        class="flex items-center gap-1 font-medium text-primary-500 hover:underline"
        rel="noopener noreferrer"
        target="_blank"
        title="En savoir plus sur les limites - nouvelle fenêtre"
      >
        En savoir plus sur les limites
        <IconArrowRight :size="16" aria-hidden="true" />
      </a>
    </div>
  </section>
</template>

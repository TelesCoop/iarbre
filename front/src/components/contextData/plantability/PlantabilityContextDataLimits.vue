<script lang="ts" setup>
import IconUndergroundParking from "@/components/icons/IconUndergroundParking.vue"
import IconCrosswalk from "@/components/icons/IconCrosswalk.vue"
import IconStreetFurniture from "@/components/icons/IconStreetFurniture.vue"
import IconUpcomingProjects from "@/components/icons/IconUpcomingProjects.vue"
import IconWarning from "@/components/icons/IconWarning.vue"
import IconChevron from "@/components/icons/IconChevron.vue"

const limits = [
  { label: "Parkings souterrains", icon: IconUndergroundParking },
  { label: "Passages piétons", icon: IconCrosswalk },
  { label: "Mobilier urbain", icon: IconStreetFurniture },
  { label: "Projets à venir", icon: IconUpcomingProjects }
]
</script>

<template>
  <details class="group w-full rounded-md bg-gold-50 text-left" data-cy="plantability-limits">
    <summary
      class="flex cursor-pointer list-none items-center gap-2 px-3 py-2 text-sm font-medium text-brown [&::-webkit-details-marker]:hidden"
      data-cy="plantability-limits-toggle"
    >
      <IconWarning :size="16" class="shrink-0" aria-hidden="true" />
      <span class="flex-1">Limites du calque</span>
      <span class="flex items-center gap-1.5 group-open:hidden" aria-hidden="true">
        <component :is="limit.icon" v-for="limit in limits" :key="limit.label" :size="16" />
      </span>
      <IconChevron :size="16" class="shrink-0 group-open:rotate-180" aria-hidden="true" />
    </summary>
    <div class="flex flex-col gap-3 px-3 pb-3">
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
      <p class="text-xs text-brown">
        <b>Domaine privé :</b> moins de données disponibles, le calque y est souvent optimiste.
      </p>
    </div>
  </details>
</template>

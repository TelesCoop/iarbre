<script lang="ts" setup>
import { computed } from "vue"
import { formatNumber, formatSurface } from "@/utils/format"
import IconMetropoleMap from "@/components/icons/IconMetropoleMap.vue"
import type { DashboardData } from "@/types/dashboard"

const props = defineProps<{
  data: DashboardData
  interpretation: string
}>()

const summaryCards = computed(() => {
  const data = props.data
  const [vegetationValue, vegetationUnit] = formatSurface(data.vegetation.totalM2).split(" ")
  return [
    {
      label: "01 Plantabilité",
      value: formatNumber(data.plantability.averageNormalizedIndice),
      unit: "/10",
      description: "Indice moyen de plantabilité en pleine terre"
    },
    {
      label: "02 Végétation",
      value: vegetationValue,
      unit: vegetationUnit,
      description: `Végétation inventoriée, dont ${formatSurface(data.vegetation.treesSurfaceM2)} de strate haute`
    },
    {
      label: "03 Contraintes",
      value: formatNumber((data.lcz.buildingRate ?? 0) + (data.lcz.impermeableSurfaceRate ?? 0)),
      unit: "%",
      description: "De surfaces minérales imperméables"
    },
    {
      label: "04 Vulnérabilité",
      value: formatNumber(data.vulnerability.averageDay),
      unit: "/9",
      description: `Vulnérabilité à la chaleur de jour, ${formatNumber(data.vulnerability.averageNight)}/9 de nuit`
    }
  ]
})

const summarySources = [
  { label: "Plantabilité · 35 facteurs d'occupation du sol", origin: "IA·rbre" },
  { label: "Inventaire de végétation · modèle FlairHub", origin: "IGN · LIDAR THD" },
  { label: "Perméabilité des sols · Zones Climatiques Locales", origin: "CEREMA 2023" },
  { label: "Caractéristiques du bâti", origin: "BD Topo" },
  { label: "Vulnérabilité à la chaleur", origin: "Institut Paris Région" }
]
</script>

<template>
  <section
    class="flex flex-col gap-5 print:h-[208mm] print:w-[297mm] print:break-before-page print:gap-0 print:overflow-hidden print:px-[18mm] print:pt-[16mm] print:pb-[12mm]"
  >
    <div v-reveal class="flex flex-col gap-1.5">
      <h2 class="text-xl font-bold text-gray-900">Synthèse du territoire</h2>
      <p class="text-sm italic text-gray-500">Les quatre indicateurs clés en une lecture.</p>
    </div>

    <div class="flex gap-6 xl:gap-10 print:mt-6 print:min-h-0 print:flex-1 print:gap-10">
      <div class="grid flex-[3] grid-cols-1 gap-4 sm:grid-cols-2 print:gap-5">
        <div
          v-for="(card, index) in summaryCards"
          :key="card.label"
          v-reveal="index * 100"
          class="summary-card flex flex-col gap-2 rounded-xl border border-gray-200 bg-white p-4 md:p-5 print:p-5"
        >
          <span
            class="text-xs font-semibold uppercase tracking-widest text-primary-500 print:text-[0.625rem]"
          >
            {{ card.label }}
          </span>
          <p class="text-3xl font-bold leading-none text-primary-600 tabular-nums md:text-4xl">
            {{ card.value
            }}<span class="ml-0.5 text-base font-semibold text-primary-400">{{ card.unit }}</span>
          </p>
          <p class="text-xs leading-snug text-gray-500">{{ card.description }}</p>
        </div>
      </div>
      <IconMetropoleMap
        v-reveal="200"
        class="hidden min-w-0 self-center text-primary-300 xl:block xl:h-72 xl:w-auto print:block print:h-full print:w-auto print:flex-[2] print:self-auto"
      />
    </div>

    <div
      v-reveal
      class="grid grid-cols-1 gap-6 border-t border-gray-200 pt-6 md:grid-cols-2 md:gap-12 print:mt-8 print:grid-cols-2 print:pt-8"
    >
      <div>
        <h3 class="mb-3 text-sm font-bold text-gray-900">Ce que disent les données</h3>
        <p class="text-sm leading-relaxed text-gray-600">{{ interpretation }}</p>
      </div>
      <div>
        <h3 class="mb-3 text-sm font-bold text-gray-900">Sources</h3>
        <div
          v-for="source in summarySources"
          :key="source.label"
          class="flex items-baseline gap-2 py-1.5"
        >
          <span class="min-w-0 text-xs text-gray-600 print:shrink-0">{{ source.label }}</span>
          <span class="flex-1 border-b border-dotted border-gray-300" />
          <span class="shrink-0 text-xs font-semibold text-gray-700">{{ source.origin }}</span>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
@reference "@/styles/main.css";

.summary-card {
  @apply transition-shadow duration-200;
}

.summary-card:hover {
  @apply shadow-md;
}

@media print {
  .summary-card {
    @apply shadow-none;
  }
}
</style>

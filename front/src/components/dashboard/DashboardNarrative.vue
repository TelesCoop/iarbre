<script lang="ts" setup>
import { computed } from "vue"
import AppSpinner from "@/components/shared/AppSpinner.vue"
import NarrativeSection from "@/components/dashboard/NarrativeSection.vue"
import PlantabilityWidget from "@/components/dashboard/widgets/PlantabilityWidget.vue"
import HeatWidget from "@/components/dashboard/widgets/HeatWidget.vue"
import BiosphereWidget from "@/components/dashboard/widgets/BiosphereWidget.vue"
import SurfaceTypeWidget from "@/components/dashboard/widgets/SurfaceTypeWidget.vue"
import VegetationSurfaceWidget from "@/components/dashboard/widgets/VegetationSurfaceWidget.vue"
import BuildingCharacteristicsWidget from "@/components/dashboard/widgets/BuildingCharacteristicsWidget.vue"
import { useDashboardStore } from "@/stores/dashboard"
import DashboardFooter from "@/components/dashboard/DashboardFooter.vue"

const props = defineProps<{ printMode?: boolean }>()

const store = useDashboardStore()

const hasData = computed(() => store.dashboardData !== null && !store.loading)

const plantabilityFinding = computed(() => {
  if (!store.dashboardData) return ""
  const score = Math.round(store.dashboardData.plantability.averageNormalizedIndice * 10) / 10
  return `${score.toLocaleString("fr-FR")}/10 en indice moyen de plantabilité`
})

const plantabilityInterpretation = computed(() => {
  if (!store.dashboardData) return ""
  const score = Math.round(store.dashboardData.plantability.averageNormalizedIndice * 10) / 10
  if (score >= 7)
    return "Il existe de nombreux espaces qui peuvent être végétalisé, et pas seulement des espaces déjà végétalisés à densifier."
  if (score >= 5)
    return "Il existe un nombre conséquent d'espaces directement disponibles, notamment des surfaces déjà végétalisées à densifier."
  if (score >= 3)
    return "Le potentiel reste modéré, probablement principalement de la densification de végétation existante."
  return "La végétalisation est très contrainte. Les marges de manoeuvre se limitent à densifier l'existant."
})

const vegetationFinding = computed(() => {
  if (!store.dashboardData) return ""
  const totalKm2 = store.dashboardData.vegetation.totalM2 / 1_000_000
  return `${totalKm2.toLocaleString("fr-FR", { maximumFractionDigits: 1 })} km² de végétation inventoriée`
})

const vegetationInterpretation = computed(() => {
  if (!store.dashboardData) return ""
  const v = store.dashboardData.vegetation
  if (v.totalM2 < 1) return ""
  const treePct = v.treesSurfaceM2 / v.totalM2
  if (treePct > 0.5)
    return "Il y a une majorité de grands arbres. C'est rare et une zone sans doute à préserver."
  if (treePct > 0.3)
    return "La végétation est diversifiée, mais la strate haute, les arbres, restent minoritaires face aux surfaces herbacées. Les surfaces en herbe sont le plus souvent des champs cultivés, et les haies."
  return "La végétation haute est peu représentée. Le strate herbacée assure l'essentiel de la couverture verte."
})

const constraintsFinding = computed(() => {
  if (!store.dashboardData) return ""
  const lcz = store.dashboardData.lcz
  const rate = Math.round(((lcz.buildingRate ?? 0) + (lcz.impermeableSurfaceRate ?? 0)) * 10) / 10
  return `${rate.toLocaleString("fr-FR")} % de surfaces imperméables`
})

const constraintsInterpretation = computed(() => {
  if (!store.dashboardData) return ""
  const lcz = store.dashboardData.lcz
  const rate = (lcz.buildingRate ?? 0) + (lcz.impermeableSurfaceRate ?? 0)
  if (rate >= 70)
    return "L'imperméabilisation massive restreint fortement les possibilités de renaturation."
  if (rate >= 50)
    return "Les surfaces imperméables constituent un frein significatif, il faudra engager des moyens pour transformer le territoire."
  return "Le taux d'imperméabilisation laisse des marges de manoeuvre réelles pour végétaliser et transformer les espaces."
})

const riskFinding = computed(() => {
  if (!store.dashboardData) return ""
  const v = store.dashboardData.vulnerability
  const day = v.averageDay.toLocaleString("fr-FR", { maximumFractionDigits: 1 })
  const night = v.averageNight.toLocaleString("fr-FR", { maximumFractionDigits: 1 })
  return `${day}/9 de jour · ${night}/9 de nuit`
})

const summaryCards = computed(() => {
  const data = store.dashboardData
  if (!data) return []
  const km2 = (m2: number) => (m2 / 1_000_000).toLocaleString("fr-FR", { maximumFractionDigits: 2 })
  const oneDecimal = (value: number) => value.toLocaleString("fr-FR", { maximumFractionDigits: 1 })
  return [
    {
      label: "01 Plantabilité",
      value: oneDecimal(data.plantability.averageNormalizedIndice),
      unit: "/10",
      description: "Indice moyen de plantabilité en pleine terre"
    },
    {
      label: "02 Végétation",
      value: oneDecimal(data.vegetation.totalM2 / 1_000_000),
      unit: "km²",
      description: `Végétation inventoriée, dont ${km2(data.vegetation.treesSurfaceM2)} km² de strate haute`
    },
    {
      label: "03 Contraintes",
      value: oneDecimal((data.lcz.buildingRate ?? 0) + (data.lcz.impermeableSurfaceRate ?? 0)),
      unit: "%",
      description: "De surfaces minérales imperméables"
    },
    {
      label: "04 Vulnérabilité",
      value: oneDecimal(data.vulnerability.averageDay),
      unit: "/9",
      description: `Vulnérabilité à la chaleur de jour, ${oneDecimal(data.vulnerability.averageNight)}/9 de nuit`
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

const riskInterpretation = computed(() => {
  if (!store.dashboardData) return ""
  const v = store.dashboardData.vulnerability
  const diff = v.averageDay - v.averageNight
  if (diff > 0.5) return "La vulnérabilité à la chaleur est particulièrement forte en journée."
  if (diff < -0.5)
    return "La vulnérabilité à la chaleur est particulièrement forte la nuit. C'est peut être le signe d'un effet d'îlot persistant."
  return "La vulnérabilité à la chaleur n'a pas une distinction nette entre jour et nuit."
})
</script>

<template>
  <div v-if="store.loading" class="flex flex-col items-center justify-center py-20 gap-4">
    <AppSpinner size="lg" color="#426A45" />
    <p class="text-sm text-gray-500">Chargement des données...</p>
  </div>

  <div v-else-if="store.error" class="flex items-center justify-center py-20">
    <p class="text-sm text-red-500">{{ store.error }}</p>
  </div>

  <div v-else-if="hasData" class="flex flex-col gap-10 print:gap-0">
    <NarrativeSection
      section-number="01"
      title="Potentiel de végétalisation"
      question="Combien de surfaces sont disponibles immédiatement pour planter des strates hautes ?"
      :finding="plantabilityFinding"
      :interpretation="plantabilityInterpretation"
      description="Le score reflète à quel point il est possible, sans transformation, de planter un arbre en pleine terre. C'est la référence avec la contrainte la plus grande."
      source="Indice calculé par pondération de 35 facteurs d'occupation du sol : réseaux, bâti, espaces verts, plans d'eau, transport, espaces artificialisés et aménagements urbains."
      source-link="https://erasme.notion.site/Lire-le-score-de-plantabilit-33444e49a3ad8080bb66f23ad06bb6a1"
    >
      <PlantabilityWidget :data="store.dashboardData!.plantability" />
    </NarrativeSection>

    <hr class="border-gray-400 print:hidden" />

    <NarrativeSection
      section-number="02"
      title="Végétation et biodiversité"
      question="Quelle est la place des espaces naturels actuellement ?"
      :finding="vegetationFinding"
      :interpretation="vegetationInterpretation"
      description="Les arbres, la canopée, sont au service du climat urbain. C'est pourquoi il est important de pouvoir quantifier la taille de la canopée et suivre les évolutions. C'est un des axes du Plan Climat Air Energie Territorial (PCAET)."
      source="Inventaire réalisé grâce au modèle FlairHub de l'IGN sur les orthophotos de la Métropole et des relevés LIDAR THD de la métropole."
      source-link="https://erasme.notion.site/L-inventaire-du-v-g-tal-stratifi-expliqu-33644e49a3ad805d95e2de361988c45d"
    >
      <VegetationSurfaceWidget :data="store.dashboardData!.vegetation" />
      <BiosphereWidget :data="store.dashboardData!.biosphere" />
    </NarrativeSection>

    <hr class="border-gray-400 print:hidden" />

    <NarrativeSection
      section-number="03"
      title="Contraintes du territoire"
      question="Qu'est ce qui freine l'aménagement et les transformations du territoire ?"
      :finding="constraintsFinding"
      :interpretation="constraintsInterpretation"
      description="Les zones imperméabilisés sont une contrainte pour la plantation d'arbre en pleine terre, mais aussi un endroit où la chaleur va plus se stocker et augmenter les ruissellements de l'eau de pluie au détriment de l'infiltration. Néanmoins des zones de bâtie dense peuvent avoir une effet positif sur l'ombre en journée et améliorer le confort thermique dans la rue."
      source="Les données proviennent de la caractérisation des sols par le CEREMA au cours de leur étude de Zones Climatiques Locales de 2023."
      source-link="https://www.cerema.fr/fr/actualites/cerema-publie-nouvelles-donnees-surchauffe-urbaine"
    >
      <BuildingCharacteristicsWidget
        :lcz="store.dashboardData!.lcz"
        :buildings="store.dashboardData!.buildings"
      />
      <SurfaceTypeWidget :data="store.dashboardData!.lcz" />
    </NarrativeSection>

    <hr class="border-gray-400 print:hidden" />

    <NarrativeSection
      section-number="04"
      title="Risques et vulnérabilités"
      question="Quelle est la vulnérabilité à la chaleur du territoire ?"
      :finding="riskFinding"
      :interpretation="riskInterpretation"
      description="La vulnérabilité à la chaleur se définit sur trois axes : l'exposition, la sensibilité et la difficulté à faire face. On fait la distinction aussi le jour et la nuit car sur ces trois axes les choses se passent différemment."
      source="C'est une étude de l'institut Paris Région répliquée par la métropole de Lyon."
      source-link="https://erasme.notion.site/Comprendre-l-atlas-de-vuln-rabilit-la-chaleur-33644e49a3ad80878f83fa021241cbd1"
    >
      <HeatWidget :data="store.dashboardData!.vulnerability" />
    </NarrativeSection>

    <section
      v-if="props.printMode"
      class="flex h-[208mm] w-[297mm] break-before-page flex-col overflow-hidden px-[18mm] pt-[16mm] pb-[12mm]"
    >
      <h2 class="text-xl font-bold text-gray-900">Synthèse du territoire</h2>
      <p class="text-sm italic text-gray-500">Les quatre indicateurs clés en une lecture.</p>

      <div class="mt-8 grid grid-cols-4 gap-6">
        <div
          v-for="card in summaryCards"
          :key="card.label"
          class="flex flex-col gap-2 rounded-xl border border-gray-200 p-5"
        >
          <span class="text-[0.625rem] font-semibold uppercase tracking-widest text-primary-500">{{
            card.label
          }}</span>
          <p class="text-4xl font-bold leading-none text-primary-600 tabular-nums">
            {{ card.value
            }}<span class="ml-0.5 text-base font-semibold text-primary-400">{{ card.unit }}</span>
          </p>
          <p class="text-xs leading-snug text-gray-500">{{ card.description }}</p>
        </div>
      </div>

      <div class="mt-auto grid grid-cols-2 gap-12 border-t border-gray-200 pt-8">
        <div>
          <h3 class="mb-3 text-sm font-bold text-gray-900">Ce que disent les données</h3>
          <p class="text-sm leading-relaxed text-gray-600">
            {{ plantabilityInterpretation }} {{ vegetationInterpretation }}
          </p>
        </div>
        <div>
          <h3 class="mb-3 text-sm font-bold text-gray-900">Sources</h3>
          <div
            v-for="source in summarySources"
            :key="source.label"
            class="flex items-baseline gap-2 py-1.5"
          >
            <span class="shrink-0 text-xs text-gray-600">{{ source.label }}</span>
            <span class="flex-1 border-b border-dotted border-gray-300" />
            <span class="shrink-0 text-xs font-semibold text-gray-700">{{ source.origin }}</span>
          </div>
        </div>
      </div>
    </section>

    <DashboardFooter v-if="!props.printMode" />
  </div>
</template>

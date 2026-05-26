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

const store = useDashboardStore()

const hasData = computed(() => store.dashboardData !== null && !store.loading)

const plantabilityFinding = computed(() => {
  if (!store.dashboardData) return ""
  const score = Math.round(store.dashboardData.plantability.averageNormalizedIndice * 10) / 10
  return `${score.toLocaleString("fr-FR")}/10 en indice moyen de plantabilité`
})

const vegetationFinding = computed(() => {
  if (!store.dashboardData) return ""
  const totalKm2 = store.dashboardData.vegetation.totalM2 / 1_000_000
  return `${totalKm2.toLocaleString("fr-FR", { maximumFractionDigits: 1 })} km² de végétation inventoriée`
})

const constraintsFinding = computed(() => {
  if (!store.dashboardData) return ""
  const lcz = store.dashboardData.lcz
  const rate = Math.round(((lcz.buildingRate ?? 0) + (lcz.impermeableSurfaceRate ?? 0)) * 10) / 10
  return `${rate.toLocaleString("fr-FR")} % de surfaces imperméables`
})

const riskFinding = computed(() => {
  if (!store.dashboardData) return ""
  const v = store.dashboardData.vulnerability
  const day = v.averageDay.toLocaleString("fr-FR", { maximumFractionDigits: 1 })
  const night = v.averageNight.toLocaleString("fr-FR", { maximumFractionDigits: 1 })
  return `${day}/9 de jour · ${night}/9 de nuit`
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

  <div v-else-if="hasData" class="flex flex-col gap-10">
    <NarrativeSection
      section-number="01"
      title="Potentiel de végétalisation"
      question="Combien de surfaces sont disponibles immédiatement pour planter des strates hautes ?"
      :finding="plantabilityFinding"
      description="Le score de plantabilité mesure la capacité des surfaces à accueillir une végétalisation en strate haute."
    >
      <PlantabilityWidget :data="store.dashboardData!.plantability" />
    </NarrativeSection>

    <NarrativeSection
      section-number="02"
      title="Végétation et biodiversité"
      question="Quelle est la place des espaces naturels actuellement ?"
      :finding="vegetationFinding"
      description="L'inventaire stratifié répertorie la végétation existante selon trois niveaux de hauteur : haute, moyenne et basse."
    >
      <VegetationSurfaceWidget :data="store.dashboardData!.vegetation" />
      <BiosphereWidget :data="store.dashboardData!.biosphere" />
    </NarrativeSection>

    <NarrativeSection
      section-number="03"
      title="Contraintes du territoire"
      question="Quelles sont les contraintes bloquantes ?"
      :finding="constraintsFinding"
      description="Les surfaces imperméables et le bâti dense constituent les principales limites à la végétalisation."
    >
      <BuildingCharacteristicsWidget
        :lcz="store.dashboardData!.lcz"
        :buildings="store.dashboardData!.buildings"
      />
      <SurfaceTypeWidget :data="store.dashboardData!.lcz" />
    </NarrativeSection>

    <NarrativeSection
      section-number="04"
      title="Risques et vulnérabilités"
      question="À quels risques climatiques le territoire est-il exposé ?"
      :finding="riskFinding"
      description="La vulnérabilité climatique croise exposition, sensibilité et capacité d'adaptation par îlot de chaleur urbain."
    >
      <HeatWidget :data="store.dashboardData!.vulnerability" />
    </NarrativeSection>
  </div>
</template>

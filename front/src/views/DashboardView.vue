<script lang="ts" setup>
import { onMounted, computed, nextTick, watch } from "vue"
import { useRoute, useRouter } from "vue-router"
import SidebarComponent from "@/components/sidebar/SidebarComponent.vue"
import DashboardHeader from "@/components/dashboard/DashboardHeader.vue"
import DashboardNarrative from "@/components/dashboard/DashboardNarrative.vue"
import { useDashboardStore } from "@/stores/dashboard"
import { setPrintMode } from "@/utils/printMode"
import { fetchExportScope } from "@/services/pdfExportService"
import { useZoneStore, type ZonePolygon } from "@/stores/zone"
import { decodeZone, encodeZone } from "@/utils/zoneUrl"

const store = useDashboardStore()
const zoneStore = useZoneStore()
const route = useRoute()
const router = useRouter()
const printMode = computed(() => route.query.print === "1")

async function initPrintScope() {
  setPrintMode(true)
  const token = route.query.export_token as string | undefined
  let scope: {
    scale: "metropole" | "commune" | "zone"
    cityCode?: string | null
    geometry?: ZonePolygon | null
  } = { scale: "metropole" }

  if (token) {
    const stored = await fetchExportScope(token)
    if (stored) {
      scope = {
        scale: (stored.scale as typeof scope.scale) ?? "metropole",
        cityCode: (stored.city_code as string) ?? null,
        geometry: (stored.geometry as ZonePolygon) ?? null
      }
    }
  } else if (route.query.city_code) {
    scope = { scale: "commune", cityCode: route.query.city_code as string }
  }

  await store.setScopeExplicit(scope)
  await nextTick()
  requestAnimationFrame(() =>
    requestAnimationFrame(() => {
      ;(window as unknown as { __DASHBOARD_READY__: boolean }).__DASHBOARD_READY__ = true
    })
  )
}

async function initScopeFromUrl() {
  const zone = typeof route.query.zone === "string" ? decodeZone(route.query.zone) : null
  const cityCode = route.query.city_code as string | undefined
  if (zone) {
    await store.setScopeExplicit({ scale: "zone", geometry: zone })
  } else if (cityCode) {
    await store.setScopeExplicit({ scale: "commune", cityCode })
  } else if (store.hasZone) {
    store.setScale("zone")
  } else {
    store.fetchDashboardData()
  }
  watch(
    () => [store.selectedScale, store.selectedCityCode, zoneStore.drawnGeometry] as const,
    ([scale, cityCode, geometry]) => {
      const query: Record<string, string> = {}
      if (scale === "commune" && cityCode) query.city_code = cityCode
      if (scale === "zone" && geometry) query.zone = encodeZone(geometry)
      router.replace({ query })
    },
    { immediate: true }
  )
}

onMounted(() => {
  if (printMode.value) {
    initPrintScope()
  } else {
    initScopeFromUrl()
  }
})
</script>

<template>
  <div class="dashboard-view-wrapper" :class="{ 'print-mode': printMode }">
    <SidebarComponent v-if="!printMode" />
    <main class="dashboard-content scrollbar">
      <DashboardHeader :print-mode="printMode" />
      <DashboardNarrative :print-mode="printMode" />
    </main>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.dashboard-view-wrapper {
  @apply flex;
  height: 100vh;
  margin-left: 0;
}

@media (min-width: 1024px) {
  .dashboard-view-wrapper {
    margin-left: 4.5rem;
  }
}

.dashboard-content {
  @apply flex-1 overflow-y-auto;
  @apply p-4 md:p-8 lg:p-12;
  @apply bg-gray-50;
  padding-bottom: 80px;
}
</style>

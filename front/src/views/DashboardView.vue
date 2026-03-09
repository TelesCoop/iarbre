<script lang="ts" setup>
import { onMounted } from "vue"
import SidebarComponent from "@/components/sidebar/SidebarComponent.vue"
import DashboardHeader from "@/components/dashboard/DashboardHeader.vue"
import DashboardGrid from "@/components/dashboard/DashboardGrid.vue"
import { useDashboardStore } from "@/stores/dashboard"

const store = useDashboardStore()

onMounted(() => {
  store.fetchDashboardData()
})
</script>

<template>
  <div class="dashboard-view-wrapper">
    <SidebarComponent />
    <main class="dashboard-content scrollbar">
      <DashboardHeader />
      <DashboardGrid />
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
    margin-left: 64px;
  }
}

.dashboard-content {
  @apply flex-1 overflow-y-auto;
  @apply p-4 md:p-8 lg:p-12;
  @apply bg-gray-50;
  padding-bottom: 80px;
}
</style>

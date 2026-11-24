<script lang="ts" setup>
import { ref, computed } from "vue"
import { useRouter, useRoute } from "vue-router"
import { useApiPost } from "@/api"
import FeedbackPopin from "@/components/FeedbackPopin.vue"
import WelcomeMessage from "@/components/WelcomeMessage.vue"
import IconChevron from "@/components/icons/IconChevron.vue"
import IconMethodology from "@/components/icons/IconMethodology.vue"
import IconFoldedMap from "@/components/icons/IconFoldedMap.vue"
import IconDashboard from "@/components/icons/IconDashboard.vue"
import IconIarbreMark from "@/components/icons/IconIarbreMark.vue"
import IconContact from "@/components/icons/IconContact.vue"
import IconFeatures from "@/components/icons/IconFeatures.vue"
import IconGithub from "@/components/icons/IconGithub.vue"
import type { Feedback } from "@/types/map"
import { useToast } from "@/composables/useToast"
import { useMapRoute } from "@/composables/useMapRoute"
import { useAppStore } from "@/stores/app"

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()
const welcomeIsVisible = ref(false)
const toast = useToast()
const mapRoute = useMapRoute()

const isDashboard = computed(() => route.name === "dashboard")
const isMethodology = computed(() => route.name === "methodology")
const isMap = computed(() => !isDashboard.value && !isMethodology.value)

const handleContactClick = () => {
  appStore.feedbackVisible = true
}

const handleFeaturesClick = () => {
  welcomeIsVisible.value = true
}

const handleGithubClick = () => {
  window.open("https://github.com/TelesCoop/iarbre", "_blank")
}

const handleMapClick = () => {
  router.push(mapRoute.value)
}

const handleDashboardClick = () => {
  router.push({ name: "dashboard" })
}

const handleMethodologyClick = () => {
  router.push({ name: "methodology" })
}

const isSidePanelVisible = computed(() => appStore.sidePanelVisible)

const handleToggleSidePanel = () => {
  appStore.toggleSidePanel()
}

const sendFeedbackToAPI = async (data: Feedback) => {
  const { error } = await useApiPost<Feedback>("feedback/", data)
  if (error != null) {
    toast.add({
      severity: "error",
      summary: "Erreur",
      detail: "Erreur lors de l'envoi du retour. Veuillez réessayer plus tard."
    })
    return false
  }
  toast.add({
    severity: "success",
    summary: "Merci !",
    detail: "Votre retour a bien été envoyé",
    life: 5000,
    group: "br"
  })
  appStore.feedbackVisible = false
  return true
}
</script>

<template>
  <!-- Desktop sidebar -->
  <aside class="sidebar hidden lg:flex">
    <div class="sidebar-logo h-28">
      <IconIarbreMark :size="30" />
    </div>

    <button
      v-if="isMap"
      :aria-expanded="isSidePanelVisible"
      :aria-label="isSidePanelVisible ? 'Masquer le panneau' : 'Afficher le panneau'"
      class="sidebar-toggle-panel"
      @click="handleToggleSidePanel"
    >
      <IconChevron
        :direction="isSidePanelVisible ? 'left' : 'right'"
        :size="20"
        class="toggle-chevron"
      />
    </button>

    <nav class="sidebar-nav">
      <button
        :class="['sidebar-nav-button', { active: isMap }]"
        aria-label="Carte"
        @click="handleMapClick"
      >
        <IconFoldedMap :size="20" />
        <span class="sidebar-nav-label">Carte</span>
      </button>
      <button
        :class="['sidebar-nav-button', { active: isDashboard }]"
        aria-label="Tableau de bord"
        data-cy="dashboard-button"
        @click="handleDashboardClick"
      >
        <IconDashboard :size="20" />
        <span class="sidebar-nav-label">Tableau<br />de bord</span>
      </button>
      <button
        :class="['sidebar-nav-button', { active: isMethodology }]"
        aria-label="Méthodologie"
        data-cy="methodology-button"
        @click="handleMethodologyClick"
      >
        <IconMethodology :size="20" />
        <span class="sidebar-nav-label">Méthodo&shy;logie</span>
      </button>
    </nav>

    <div class="sidebar-icons">
      <button aria-label="Contact" class="sidebar-icon-button" @click="handleContactClick">
        <IconContact :size="24" />
      </button>

      <button aria-label="Features" class="sidebar-icon-button" @click="handleFeaturesClick">
        <IconFeatures :size="24" />
      </button>

      <button aria-label="GitHub" class="sidebar-icon-button" @click="handleGithubClick">
        <IconGithub :size="24" />
      </button>
    </div>
  </aside>

  <!-- Mobile bottom bar -->
  <div class="mobile-bottom-bar lg:hidden!">
    <div class="mobile-bar-logo">
      <IconIarbreMark :size="24" />
    </div>

    <div class="mobile-bar-icons">
      <button
        :class="['mobile-bar-button', { 'mobile-bar-button-active': isMap }]"
        aria-label="Carte"
        @click="handleMapClick"
      >
        <IconFoldedMap :size="20" />
      </button>
      <button
        :class="['mobile-bar-button', { 'mobile-bar-button-active': isDashboard }]"
        aria-label="Tableau de bord"
        data-cy="dashboard-button-mobile"
        @click="handleDashboardClick"
      >
        <IconDashboard :size="20" />
      </button>
      <button
        :class="['mobile-bar-button', { 'mobile-bar-button-active': isMethodology }]"
        aria-label="Méthodologie"
        data-cy="methodology-button-mobile"
        @click="handleMethodologyClick"
      >
        <IconMethodology :size="20" />
      </button>

      <button aria-label="Contact" class="mobile-bar-button" @click="handleContactClick">
        <IconContact :size="20" />
      </button>

      <button aria-label="Features" class="mobile-bar-button" @click="handleFeaturesClick">
        <IconFeatures :size="20" />
      </button>

      <button aria-label="GitHub" class="mobile-bar-button" @click="handleGithubClick">
        <IconGithub :size="20" />
      </button>
    </div>
  </div>

  <WelcomeMessage v-model="welcomeIsVisible" />

  <FeedbackPopin v-model="appStore.feedbackVisible" @submit-feedback="sendFeedbackToAPI" />
</template>

<style scoped>
@reference "@/styles/main.css";

.sidebar {
  @apply fixed top-0 h-screen flex-col;
  @apply border-r-primary-300 border-r-1;
  @apply bg-white z-50;
  left: 0;
  width: 4.5rem;
}

.sidebar-logo {
  @apply bg-white flex items-center justify-center text-primary-500;
  @apply border-b-1 border-[#426A45];
  flex-shrink: 0;
}

.sidebar-icons {
  @apply flex flex-col items-center;
  @apply bg-primary-500;
  @apply mt-auto;
  gap: 1rem;
  padding: 1.5rem 0 5rem;
  flex-shrink: 0;
}

.sidebar-icon-button {
  @apply flex items-center justify-center cursor-pointer text-white;
  @apply bg-transparent border-none p-0;
  @apply transition-opacity hover:opacity-80;
  width: 1.5rem;
  height: 1.5rem;
}

.sidebar-toggle-panel {
  @apply hidden lg:flex items-center justify-center cursor-pointer;
  @apply bg-gray-100 border-none;
  @apply transition-all duration-200;
  @apply hover:bg-gray-200;
  width: 100%;
  height: 2.5rem;
  flex-shrink: 0;
}

.sidebar-nav {
  @apply hidden lg:flex flex-col;
  @apply border-b-1 border-gray-200;
  flex-shrink: 0;
}

.sidebar-nav-button {
  @apply flex flex-col items-center justify-center cursor-pointer;
  @apply bg-gray-50 border-none text-gray-500;
  @apply transition-all duration-200;
  @apply hover:bg-primary-50 hover:text-primary-600;
  width: 100%;
  height: 4rem;
  gap: 0.25rem;
}

.sidebar-nav-button.active {
  @apply bg-primary-100 text-primary-700;
  @apply border-l-2 border-l-primary-600;
}

.sidebar-nav-label {
  @apply text-center leading-tight;
  font-size: 0.5625rem;
  font-weight: 500;
}

.toggle-chevron {
  @apply text-gray-600;
  transition: transform 0.3s ease-out;
}

.mobile-bottom-bar {
  @apply fixed bottom-0 left-0 right-0 z-50;
  @apply flex items-center justify-between px-4;
  @apply bg-[#426A45];
  height: var(--mobile-bar-height);
}

.mobile-bar-logo {
  @apply flex items-center justify-center text-white;
}

.mobile-bar-icons {
  @apply flex items-center gap-4;
}

.mobile-bar-button {
  @apply flex items-center justify-center cursor-pointer;
  @apply bg-transparent border-none p-2;
  @apply text-white;
  @apply transition-opacity hover:opacity-80;
}

.mobile-bar-button-active {
  @apply opacity-100 bg-white/20 rounded-lg;
}
</style>

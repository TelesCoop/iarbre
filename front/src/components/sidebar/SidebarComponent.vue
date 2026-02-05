<script lang="ts" setup>
import { ref, computed } from "vue"
import { useApiPost } from "@/api"
import FeedbackPopin from "@/components/FeedbackPopin.vue"
import WelcomeMessage from "@/components/WelcomeMessage.vue"
import IconChevron from "@/components/icons/IconChevron.vue"
import type { Feedback } from "@/types/map"
import { useToast } from "@/composables/useToast"
import { useAppStore } from "@/stores/app"

const appStore = useAppStore()
const feedbackIsVisible = ref(false)
const welcomeIsVisible = ref(false)
const toast = useToast()

const handleContactClick = () => {
  feedbackIsVisible.value = true
}

const handleFeaturesClick = () => {
  welcomeIsVisible.value = true
}

const handleGithubClick = () => {
  window.open("https://github.com/TelesCoop/iarbre", "_blank")
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
  feedbackIsVisible.value = false
  return true
}
</script>

<template>
  <!-- Desktop sidebar -->
  <aside class="sidebar hidden lg:flex">
    <div class="sidebar-logo h-28">
      <svg
        fill="none"
        height="30"
        viewBox="0 0 25 30"
        width="25"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M21.6679 14.6619C21.6679 14.1425 21.2435 13.718 20.7241 13.718C20.2047 13.718 19.7803 14.1425 19.7803 14.6619C19.7803 15.1812 20.2047 15.6057 20.7241 15.6057C21.2435 15.6057 21.6679 15.1812 21.6679 14.6619Z"
          fill="#426A45"
        />
        <path
          d="M17.8931 8.22974C17.3737 8.22974 16.9492 8.65421 16.9492 9.17357C16.9492 9.69293 17.3737 10.1174 17.8931 10.1174C18.4124 10.1174 18.8369 9.69293 18.8369 9.17357C18.8369 8.65421 18.4124 8.22974 17.8931 8.22974Z"
          fill="#426A45"
        />
        <path
          d="M17.8931 10.9714C17.3737 10.9714 16.9492 11.3959 16.9492 11.9153C16.9492 12.4346 17.3737 12.8591 17.8931 12.8591C18.4124 12.8591 18.8369 12.4346 18.8369 11.9153C18.8369 11.3959 18.4124 10.9714 17.8931 10.9714Z"
          fill="#426A45"
        />
        <path
          d="M17.8931 13.718C17.3737 13.718 16.9492 14.1425 16.9492 14.6619C16.9492 15.1812 17.3737 15.6057 17.8931 15.6057C18.4124 15.6057 18.8369 15.1812 18.8369 14.6619C18.8369 14.1425 18.4124 13.718 17.8931 13.718Z"
          fill="#426A45"
        />
        <path
          d="M17.8931 16.4597C17.3737 16.4597 16.9492 16.8842 16.9492 17.4035C16.9492 17.9229 17.3737 18.3474 17.8931 18.3474C18.4124 18.3474 18.8369 17.9229 18.8369 17.4035C18.8369 16.8842 18.4124 16.4597 17.8931 16.4597Z"
          fill="#426A45"
        />
        <path
          d="M16 9.17357C16 8.65421 15.5755 8.22974 15.0561 8.22974C14.5368 8.22974 14.1123 8.65421 14.1123 9.17357C14.1123 9.69293 14.5368 10.1174 15.0561 10.1174C15.5755 10.1174 16 9.69293 16 9.17357Z"
          fill="#426A45"
        />
        <path
          d="M16 11.9153C16 11.3959 15.5755 10.9714 15.0561 10.9714C14.5368 10.9714 14.1123 11.3959 14.1123 11.9153C14.1123 12.4346 14.5368 12.8591 15.0561 12.8591C15.5755 12.8591 16 12.4346 16 11.9153Z"
          fill="#426A45"
        />
        <path
          d="M16 14.6619C16 14.1425 15.5755 13.718 15.0561 13.718C14.5368 13.718 14.1123 14.1425 14.1123 14.6619C14.1123 15.1812 14.5368 15.6057 15.0561 15.6057C15.5755 15.6057 16 15.1812 16 14.6619Z"
          fill="#426A45"
        />
        <path
          d="M16 20.1452C16 19.6259 15.5755 19.2014 15.0561 19.2014C14.5368 19.2014 14.1123 19.6259 14.1123 20.1452C14.1123 20.6646 14.5368 21.0891 15.0561 21.0891C15.5755 21.0891 16 20.6646 16 20.1452Z"
          fill="#426A45"
        />
        <path
          d="M12.2251 8.22974C11.7057 8.22974 11.2812 8.65421 11.2812 9.17357C11.2812 9.69293 11.7057 10.1174 12.2251 10.1174C12.7444 10.1174 13.1689 9.69293 13.1689 9.17357C13.1689 8.65421 12.7444 8.22974 12.2251 8.22974Z"
          fill="#426A45"
        />
        <path
          d="M12.2251 10.9714C11.7057 10.9714 11.2812 11.3959 11.2812 11.9153C11.2812 12.4346 11.7057 12.8591 12.2251 12.8591C12.7444 12.8591 13.1689 12.4346 13.1689 11.9153C13.1689 11.3959 12.7444 10.9714 12.2251 10.9714Z"
          fill="#426A45"
        />
        <path
          d="M12.2251 13.718C11.7057 13.718 11.2812 14.1425 11.2812 14.6619C11.2812 15.1812 11.7057 15.6057 12.2251 15.6057C12.7444 15.6057 13.1689 15.1812 13.1689 14.6619C13.1689 14.1425 12.7444 13.718 12.2251 13.718Z"
          fill="#426A45"
        />
        <path
          d="M12.2251 16.4597C11.7057 16.4597 11.2812 16.8842 11.2812 17.4035C11.2812 17.9229 11.7057 18.3474 12.2251 18.3474C12.7444 18.3474 13.1689 17.9229 13.1689 17.4035C13.1689 16.8842 12.7444 16.4597 12.2251 16.4597Z"
          fill="#426A45"
        />
        <path
          d="M12.2251 19.2014C11.7057 19.2014 11.2812 19.6259 11.2812 20.1452C11.2812 20.6646 11.7057 21.0891 12.2251 21.0891C12.7444 21.0891 13.1689 20.6646 13.1689 20.1452C13.1689 19.6259 12.7444 19.2014 12.2251 19.2014Z"
          fill="#426A45"
        />
        <path
          d="M12.2251 21.9429C11.7057 21.9429 11.2812 22.3673 11.2812 22.8867C11.2812 23.4061 11.7057 23.8305 12.2251 23.8305C12.7444 23.8305 13.1689 23.4061 13.1689 22.8867C13.1689 22.3673 12.7444 21.9429 12.2251 21.9429Z"
          fill="#426A45"
        />
        <path
          d="M12.2251 24.6895C11.7057 24.6895 11.2812 25.1139 11.2812 25.6333C11.2812 26.1526 11.7057 26.5771 12.2251 26.5771C12.7444 26.5771 13.1689 26.1526 13.1689 25.6333C13.1689 25.1139 12.7444 24.6895 12.2251 24.6895Z"
          fill="#426A45"
        />
        <path
          d="M9.39403 8.22974C8.87467 8.22974 8.4502 8.65421 8.4502 9.17357C8.4502 9.69293 8.87467 10.1174 9.39403 10.1174C9.91338 10.1174 10.3379 9.69293 10.3379 9.17357C10.3379 8.65421 9.91338 8.22974 9.39403 8.22974Z"
          fill="#426A45"
        />
        <path
          d="M9.39403 10.9714C8.87467 10.9714 8.4502 11.3959 8.4502 11.9153C8.4502 12.4346 8.87467 12.8591 9.39403 12.8591C9.91338 12.8591 10.3379 12.4346 10.3379 11.9153C10.3379 11.3959 9.91338 10.9714 9.39403 10.9714Z"
          fill="#426A45"
        />
        <path
          d="M9.39403 13.718C8.87467 13.718 8.4502 14.1425 8.4502 14.6619C8.4502 15.1812 8.87467 15.6057 9.39403 15.6057C9.91338 15.6057 10.3379 15.1812 10.3379 14.6619C10.3379 14.1425 9.91338 13.718 9.39403 13.718Z"
          fill="#426A45"
        />
        <path
          d="M9.39403 19.2014C8.87467 19.2014 8.4502 19.6259 8.4502 20.1452C8.4502 20.6646 8.87467 21.0891 9.39403 21.0891C9.91338 21.0891 10.3379 20.6646 10.3379 20.1452C10.3379 19.6259 9.91338 19.2014 9.39403 19.2014Z"
          fill="#426A45"
        />
        <path
          d="M6.562 8.22974C6.04264 8.22974 5.61816 8.65421 5.61816 9.17357C5.61816 9.69293 6.04264 10.1174 6.562 10.1174C7.08135 10.1174 7.50583 9.69293 7.50583 9.17357C7.50583 8.65421 7.08135 8.22974 6.562 8.22974Z"
          fill="#426A45"
        />
        <path
          d="M6.562 10.9714C6.04264 10.9714 5.61816 11.3959 5.61816 11.9153C5.61816 12.4346 6.04264 12.8591 6.562 12.8591C7.08135 12.8591 7.50583 12.4346 7.50583 11.9153C7.50583 11.3959 7.08135 10.9714 6.562 10.9714Z"
          fill="#426A45"
        />
        <path
          d="M6.562 13.718C6.04264 13.718 5.61816 14.1425 5.61816 14.6619C5.61816 15.1812 6.04264 15.6057 6.562 15.6057C7.08135 15.6057 7.50583 15.1812 7.50583 14.6619C7.50583 14.1425 7.08135 13.718 6.562 13.718Z"
          fill="#426A45"
        />
        <path
          d="M6.562 16.4597C6.04264 16.4597 5.61816 16.8842 5.61816 17.4035C5.61816 17.9229 6.04264 18.3474 6.562 18.3474C7.08135 18.3474 7.50583 17.9229 7.50583 17.4035C7.50583 16.8842 7.08135 16.4597 6.562 16.4597Z"
          fill="#426A45"
        />
        <path
          d="M4.66891 14.6619C4.66891 14.1425 4.24444 13.718 3.72508 13.718C3.20572 13.718 2.78125 14.1425 2.78125 14.6619C2.78125 15.1812 3.20572 15.6057 3.72508 15.6057C4.24444 15.6057 4.66891 15.1812 4.66891 14.6619Z"
          fill="#426A45"
        />
        <path
          d="M16 6.43211C16 5.91276 15.5755 5.48828 15.0561 5.48828C14.5368 5.48828 14.1123 5.91276 14.1123 6.43211C14.1123 6.95147 14.5368 7.37595 15.0561 7.37595C15.5755 7.37595 16 6.95147 16 6.43211Z"
          fill="#426A45"
        />
        <path
          d="M12.2251 2.7417C11.7057 2.7417 11.2812 3.16617 11.2812 3.68553C11.2812 4.20489 11.7057 4.62936 12.2251 4.62936C12.7444 4.62936 13.1689 4.20489 13.1689 3.68553C13.1689 3.16617 12.7444 2.7417 12.2251 2.7417Z"
          fill="#426A45"
        />
        <path
          d="M12.2251 5.48315C11.7057 5.48315 11.2812 5.90763 11.2812 6.42699C11.2812 6.94634 11.7057 7.37082 12.2251 7.37082C12.7444 7.37082 13.1689 6.94634 13.1689 6.42699C13.1689 5.90763 12.7444 5.48315 12.2251 5.48315Z"
          fill="#426A45"
        />
        <path
          d="M9.39403 5.48315C8.87467 5.48315 8.4502 5.90763 8.4502 6.42699C8.4502 6.94634 8.87467 7.37082 9.39403 7.37082C9.91338 7.37082 10.3379 6.94634 10.3379 6.42699C10.3379 5.90763 9.91338 5.48315 9.39403 5.48315Z"
          fill="#426A45"
        />
      </svg>
    </div>

    <button
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

    <div class="sidebar-icons">
      <button aria-label="Contact" class="sidebar-icon-button" @click="handleContactClick">
        <svg
          fill="none"
          height="24"
          viewBox="0 0 24 24"
          width="24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            clip-rule="evenodd"
            d="M8.61097 18.5931L4.8 21L5.46774 16.7827C3.88371 15.3227 3 13.2947 3 11.0526C3 6.60529 6.47715 3 12 3C17.5228 3 21 6.60529 21 11.0526C21 15.5 17.5228 19.1053 12 19.1053C10.7622 19.1053 9.62714 18.9242 8.61097 18.5931Z"
            fill-rule="evenodd"
            stroke="white"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
          />
          <path
            d="M9 9H15"
            stroke="white"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
          />
          <path
            d="M9 13H12"
            stroke="white"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
          />
        </svg>
      </button>

      <button aria-label="Features" class="sidebar-icon-button" @click="handleFeaturesClick">
        <svg
          fill="none"
          height="24"
          viewBox="0 0 24 24"
          width="24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            clip-rule="evenodd"
            d="M12 3L20 6.6V17.4L12 21L4 17.4V6.6L12 3Z"
            fill-rule="evenodd"
            stroke="white"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
          />
          <path
            d="M12.01 16.5H12"
            stroke="white"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
          />
          <path
            d="M12 13.75V12.8929C13.5188 12.8929 14.75 11.7416 14.75 10.3214C14.75 8.90127 13.5188 7.75 12 7.75C10.4812 7.75 9.25 8.90127 9.25 10.3214"
            stroke="white"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
          />
        </svg>
      </button>

      <button aria-label="GitHub" class="sidebar-icon-button" @click="handleGithubClick">
        <svg
          fill="none"
          height="24"
          viewBox="0 0 24 24"
          width="24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <mask
            id="mask0_811_2045"
            height="21"
            maskUnits="userSpaceOnUse"
            style="mask-type: luminance"
            width="20"
            x="3"
            y="1"
          >
            <path d="M23 1.40381H3V21.5638H23V1.40381Z" fill="white" />
          </mask>
          <g mask="url(#mask0_811_2045)">
            <path
              clip-rule="evenodd"
              d="M13 1.40381C7.475 1.40381 3 5.91461 3 11.4838C3 15.9442 5.8625 19.7116 9.8375 21.0472C10.3375 21.1354 10.525 20.833 10.525 20.5684C10.525 20.329 10.5125 19.5352 10.5125 18.691C8 19.1572 7.35 18.0736 7.15 17.5066C7.0375 17.2168 6.55 16.3222 6.125 16.0828C5.775 15.8938 5.275 15.4276 6.1125 15.415C6.9 15.4024 7.4625 16.1458 7.65 16.4482C8.55 17.9728 9.9875 17.5444 10.5625 17.2798C10.65 16.6246 10.9125 16.1836 11.2 15.9316C8.975 15.6796 6.65 14.8102 6.65 10.9546C6.65 9.85844 7.0375 8.95121 7.675 8.24561C7.575 7.99361 7.225 6.96041 7.775 5.57441C7.775 5.57441 8.6125 5.30981 10.525 6.60761C11.325 6.38081 12.175 6.26741 13.025 6.26741C13.875 6.26741 14.725 6.38081 15.525 6.60761C17.4375 5.29721 18.275 5.57441 18.275 5.57441C18.825 6.96041 18.475 7.99361 18.375 8.24561C19.0125 8.95121 19.4 9.84584 19.4 10.9546C19.4 14.8228 17.0625 15.6796 14.8375 15.9316C15.2 16.2466 15.5125 16.8514 15.5125 17.7964C15.5125 19.1446 15.5 20.2282 15.5 20.5684C15.5 20.833 15.6875 21.148 16.1875 21.0472C20.1375 19.7116 23 15.9316 23 11.4838C23 5.91461 18.525 1.40381 13 1.40381Z"
              fill="white"
              fill-rule="evenodd"
            />
          </g>
        </svg>
      </button>
    </div>
  </aside>

  <!-- Mobile bottom bar -->
  <div class="mobile-bottom-bar lg:hidden!">
    <button aria-label="Contact" class="mobile-bar-button" @click="handleContactClick">
      <svg
        fill="none"
        height="20"
        viewBox="0 0 24 24"
        width="20"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          clip-rule="evenodd"
          d="M8.61097 18.5931L4.8 21L5.46774 16.7827C3.88371 15.3227 3 13.2947 3 11.0526C3 6.60529 6.47715 3 12 3C17.5228 3 21 6.60529 21 11.0526C21 15.5 17.5228 19.1053 12 19.1053C10.7622 19.1053 9.62714 18.9242 8.61097 18.5931Z"
          fill-rule="evenodd"
          stroke="currentColor"
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
        />
        <path
          d="M9 9H15"
          stroke="currentColor"
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
        />
        <path
          d="M9 13H12"
          stroke="currentColor"
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
        />
      </svg>
    </button>

    <button aria-label="Features" class="mobile-bar-button" @click="handleFeaturesClick">
      <svg
        fill="none"
        height="20"
        viewBox="0 0 24 24"
        width="20"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          clip-rule="evenodd"
          d="M12 3L20 6.6V17.4L12 21L4 17.4V6.6L12 3Z"
          fill-rule="evenodd"
          stroke="currentColor"
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
        />
        <path
          d="M12.01 16.5H12"
          stroke="currentColor"
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
        />
        <path
          d="M12 13.75V12.8929C13.5188 12.8929 14.75 11.7416 14.75 10.3214C14.75 8.90127 13.5188 7.75 12 7.75C10.4812 7.75 9.25 8.90127 9.25 10.3214"
          stroke="currentColor"
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
        />
      </svg>
    </button>

    <button aria-label="GitHub" class="mobile-bar-button" @click="handleGithubClick">
      <svg
        fill="none"
        height="20"
        viewBox="0 0 24 24"
        width="20"
        xmlns="http://www.w3.org/2000/svg"
      >
        <mask
          id="mask_mobile"
          height="21"
          maskUnits="userSpaceOnUse"
          style="mask-type: luminance"
          width="20"
          x="3"
          y="1"
        >
          <path d="M23 1.40381H3V21.5638H23V1.40381Z" fill="white" />
        </mask>
        <g mask="url(#mask_mobile)">
          <path
            clip-rule="evenodd"
            d="M13 1.40381C7.475 1.40381 3 5.91461 3 11.4838C3 15.9442 5.8625 19.7116 9.8375 21.0472C10.3375 21.1354 10.525 20.833 10.525 20.5684C10.525 20.329 10.5125 19.5352 10.5125 18.691C8 19.1572 7.35 18.0736 7.15 17.5066C7.0375 17.2168 6.55 16.3222 6.125 16.0828C5.775 15.8938 5.275 15.4276 6.1125 15.415C6.9 15.4024 7.4625 16.1458 7.65 16.4482C8.55 17.9728 9.9875 17.5444 10.5625 17.2798C10.65 16.6246 10.9125 16.1836 11.2 15.9316C8.975 15.6796 6.65 14.8102 6.65 10.9546C6.65 9.85844 7.0375 8.95121 7.675 8.24561C7.575 7.99361 7.225 6.96041 7.775 5.57441C7.775 5.57441 8.6125 5.30981 10.525 6.60761C11.325 6.38081 12.175 6.26741 13.025 6.26741C13.875 6.26741 14.725 6.38081 15.525 6.60761C17.4375 5.29721 18.275 5.57441 18.275 5.57441C18.825 6.96041 18.475 7.99361 18.375 8.24561C19.0125 8.95121 19.4 9.84584 19.4 10.9546C19.4 14.8228 17.0625 15.6796 14.8375 15.9316C15.2 16.2466 15.5125 16.8514 15.5125 17.7964C15.5125 19.1446 15.5 20.2282 15.5 20.5684C15.5 20.833 15.6875 21.148 16.1875 21.0472C20.1375 19.7116 23 15.9316 23 11.4838C23 5.91461 18.525 1.40381 13 1.40381Z"
            fill="currentColor"
            fill-rule="evenodd"
          />
        </g>
      </svg>
    </button>
  </div>

  <WelcomeMessage v-model="welcomeIsVisible" />

  <FeedbackPopin
    :model-value="feedbackIsVisible"
    @close="feedbackIsVisible = false"
    @submit-feedback="sendFeedbackToAPI"
  />
</template>

<style scoped>
@reference "@/styles/main.css";

.sidebar {
  @apply fixed top-0 h-screen flex-col;
  @apply border-r-primary-300 border-r-1;
  @apply bg-white z-50;
  left: 0;
  width: 64px;
}

.sidebar-logo {
  @apply bg-white flex items-center justify-center;
  @apply border-b-1 border-[#426A45];
  flex-shrink: 0;
}

.sidebar-icons {
  @apply flex flex-col items-center;
  @apply bg-[#426A45];
  @apply mt-auto;
  gap: 16px;
  padding: 24px 0;
  flex-shrink: 0;
}

.sidebar-icon-button {
  @apply flex items-center justify-center cursor-pointer;
  @apply bg-transparent border-none p-0;
  @apply transition-opacity hover:opacity-80;
  width: 24px;
  height: 24px;
}

.sidebar-toggle-panel {
  @apply hidden lg:flex items-center justify-center cursor-pointer;
  @apply bg-gray-100 border-none;
  @apply transition-all duration-200;
  @apply hover:bg-gray-200;
  width: 100%;
  height: 40px;
  flex-shrink: 0;
}

.toggle-chevron {
  @apply text-gray-600;
  transition: transform 0.3s ease-out;
}

.mobile-bottom-bar {
  @apply fixed bottom-0 left-0 right-0 z-50;
  @apply flex items-center justify-center gap-6;
  @apply bg-[#426A45];
  height: 56px;
}

.mobile-bar-button {
  @apply flex items-center justify-center cursor-pointer;
  @apply bg-transparent border-none p-2;
  @apply text-white;
  @apply transition-opacity hover:opacity-80;
}
</style>

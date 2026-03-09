<script lang="ts" setup>
import { ref } from "vue"
import IconIarbreLogo from "@/components/icons/IconIarbreLogo.vue"

const isPopoverVisible = ref(false)
const attributionHTML = ref("1.44M habitants. 534 km² superficie")

const toggleAttribution = () => {
  isPopoverVisible.value = !isPopoverVisible.value
}

const closePopover = () => {
  isPopoverVisible.value = false
}
</script>

<template>
  <div>
    <div
      class="bg-primary-500 font-sans flex px-4 pt-4 pb-4 flex-col items-start gap-2.5 flex-shrink-0 self-stretch h-28"
      data-cy="map-sidepanel-header"
    >
      <a
        class="flex items-center"
        href="https://iarbre.fr"
        rel="noopener noreferrer"
        target="_blank"
      >
        <IconIarbreLogo :width="85" class="text-white" />
      </a>
      <div class="flex items-center gap-2">
        <h2 class="text-xl text-white font-semibold">Métropole de Lyon</h2>
        <div class="relative">
          <button aria-label="Informations" class="info-button" @click="toggleAttribution">
            <span class="text-xs font-bold">i</span>
          </button>

          <!-- Popover positioned relative to button -->
          <div v-if="isPopoverVisible" class="attribution-popover" data-cy="attribution-popover">
            <!-- eslint-disable-next-line vue/no-v-html -->
            <div v-if="attributionHTML" v-html="attributionHTML"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Backdrop to close popover -->
    <div v-if="isPopoverVisible" class="fixed inset-0 z-40" @click="closePopover"></div>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.info-button {
  @apply flex items-center justify-center w-5 h-5 rounded-full;
  @apply border border-white text-white;
  @apply hover:bg-white hover:text-primary-500;
  @apply transition-colors cursor-pointer;
}

.attribution-popover {
  @apply absolute bg-white rounded-lg  border border-gray-200 p-3 text-sm;
  @apply z-50 whitespace-nowrap;
  top: -8px;
  left: calc(100% + 8px);
}

.attribution-popover::before {
  content: "";
  @apply absolute w-2 h-2 bg-white border-l border-b border-gray-200;
  top: 12px;
  left: -5px;
  transform: rotate(45deg);
}
</style>

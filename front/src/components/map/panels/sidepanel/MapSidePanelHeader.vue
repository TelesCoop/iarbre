<script lang="ts" setup>
import { ref } from "vue"
import IconIarbreLogo from "@/components/icons/IconIarbreLogo.vue"

const isPopoverVisible = ref(false)
const attributionHTML = ref("1.44M habitants. 534 km² superficie")
const infoButtonRef = ref<HTMLButtonElement | null>(null)

const popoverStyle = () => {
  if (!infoButtonRef.value) return {}
  const rect = infoButtonRef.value.getBoundingClientRect()
  return { top: `${rect.top - 8}px`, left: `${rect.right + 8}px` }
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
        <button
          ref="infoButtonRef"
          aria-label="Informations"
          class="info-button"
          @click="isPopoverVisible = !isPopoverVisible"
        >
          <span class="text-xs font-bold">i</span>
        </button>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="isPopoverVisible" class="fixed inset-0 z-[100]" @click="isPopoverVisible = false">
        <div
          class="attribution-popover"
          :style="popoverStyle()"
          data-cy="attribution-popover"
          @click.stop
        >
          <!-- eslint-disable-next-line vue/no-v-html -->
          <div v-if="attributionHTML" v-html="attributionHTML"></div>
        </div>
      </div>
    </Teleport>
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
  @apply fixed bg-white rounded-lg border border-gray-200 p-3 text-sm;
  @apply whitespace-nowrap;
}

.attribution-popover::before {
  content: "";
  @apply absolute w-2 h-2 bg-white border-l border-b border-gray-200;
  top: 12px;
  left: -5px;
  transform: rotate(45deg);
}
</style>

<script lang="ts" setup>
import { ref } from "vue"
import IconShare from "@/components/icons/IconShare.vue"
import MapShareDialog from "@/components/map/share/MapShareDialog.vue"

defineProps<{
  mapId: string
}>()

const isDialogVisible = ref(false)
</script>

<template>
  <button
    aria-haspopup="dialog"
    class="flex items-center justify-center gap-1.5 py-1.5 px-2 lg:px-2.5 bg-gold-300 text-primary-900 border border-gold-300 hover:bg-gold-500 hover:border-gold-500 rounded-lg pointer-events-auto font-sans shrink-0 cursor-pointer transition-all"
    data-cy="share-view-button"
    type="button"
    @click="isDialogVisible = true"
  >
    <IconShare class="shrink-0" :size="14" />
    <span class="text-xs lg:text-sm font-medium whitespace-nowrap">Partager cette vue</span>
  </button>
  <MapShareDialog v-model="isDialogVisible" :map-id="mapId" />
</template>

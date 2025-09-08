<template>
  <button class="flex flex-col items-center" @click="$emit('toggle')">
    <span class="text-xs text-primary-500 font-bold underline">
      {{ isExpanded ? "Masquer les détails" : "Afficher les détails" }}
    </span>
  </button>
</template>

<script lang="ts" setup>
interface Props {
  isExpanded: boolean
}

defineProps<Props>()
defineEmits<{
  toggle: []
}>()
</script>

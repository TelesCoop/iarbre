<template>
  <button class="text-lg flex flex-col items-center" @click="$emit('toggle')">
    <span class="text-sm">
      {{ isExpanded ? "Masquer les détails" : "Afficher les détails" }}
    </span>
    <span class="text-lg"> {{ isExpanded ? "▲" : "▼" }} </span>
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

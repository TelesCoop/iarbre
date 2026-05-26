<script lang="ts" setup>
interface Props {
  sectionNumber: string
  title: string
  question: string
  finding?: string
  description?: string
}

defineProps<Props>()
</script>

<template>
  <section class="flex flex-col gap-5">
    <div class="flex flex-col gap-1.5 pb-4 border-b border-gray-200">
      <div class="flex items-baseline gap-2">
        <span class="text-xs font-mono font-semibold text-gray-400 tabular-nums shrink-0">{{
          sectionNumber
        }}</span>
        <span class="text-primary-400 text-xs shrink-0">↘</span>
        <h2 class="text-xl font-bold text-gray-900">{{ title }}</h2>
      </div>
      <p class="text-sm text-gray-500 italic">{{ question }}</p>
      <p v-if="finding" class="font-serif text-2xl font-bold text-gray-900 mt-1">{{ finding }}</p>
      <p v-if="description" class="text-sm text-gray-500">{{ description }}</p>
    </div>
    <div class="grid grid-cols-1 gap-4 md:grid-cols-2 md:gap-6">
      <slot />
    </div>
  </section>
</template>

<script lang="ts" setup>
interface Props {
  sectionNumber: string
  title: string
  question: string
  finding?: string
  interpretation?: string
  description?: string
  source?: string
  sourceLink?: string
}

defineProps<Props>()
</script>

<template>
  <section
    class="flex flex-col gap-5 print:grid print:h-[208mm] print:w-[297mm] print:break-before-page print:grid-cols-[42%_1fr] print:grid-rows-[auto_1fr_auto] print:gap-x-10 print:gap-y-0 print:overflow-hidden print:px-[18mm] print:pt-[16mm] print:pb-[12mm]"
  >
    <div class="flex flex-col gap-1.5 pb-4 border-b border-gray-200 print:contents">
      <div class="flex flex-col gap-1.5 print:col-span-2 print:pb-6">
        <div class="flex items-baseline gap-2">
          <span class="text-xs font-mono font-semibold text-gray-400 tabular-nums shrink-0">{{
            sectionNumber
          }}</span>
          <span class="text-primary-400 text-xs shrink-0">↘</span>
          <h2 class="text-xl font-bold text-gray-900">{{ title }}</h2>
        </div>
        <p class="text-sm text-gray-500 italic">{{ question }}</p>
      </div>
      <div class="flex flex-col gap-1.5 print:min-h-0 print:gap-3">
        <p
          v-if="finding"
          class="text-3xl font-bold text-primary-600 tabular-nums mt-1 leading-tight"
        >
          {{ finding }}
        </p>
        <p
          v-if="interpretation"
          class="text-base font-semibold text-gray-800 leading-relaxed max-w-[68.75%] print:max-w-full"
        >
          {{ interpretation }}
        </p>
        <p v-if="description" class="text-sm text-gray-600 leading-relaxed">{{ description }}</p>
      </div>
    </div>
    <div
      class="grid grid-cols-1 gap-6 md:grid-cols-2 md:[&>*:only-child]:col-span-2 print:min-h-0 print:grid-cols-1 print:content-center"
    >
      <slot />
    </div>
    <p
      v-if="source"
      class="text-xs text-gray-600 italic border-t border-gray-100 pt-3 print:col-span-2 print:self-end print:border-0"
    >
      {{ source }}
      <br />
      <a
        v-if="sourceLink"
        :href="sourceLink"
        target="_blank"
        rel="noopener noreferrer"
        class="underline hover:text-gray-800"
        >En savoir plus.</a
      >
    </p>
  </section>
</template>

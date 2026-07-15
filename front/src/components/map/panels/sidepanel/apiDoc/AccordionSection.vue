<script lang="ts" setup>
withDefaults(
  defineProps<{
    open: boolean
    bodyClass?: string
  }>(),
  { bodyClass: "px-3 py-3 space-y-4" }
)
defineEmits<{ (e: "toggle"): void }>()
</script>

<template>
  <div class="border border-gray-200 rounded-md overflow-hidden">
    <button
      type="button"
      :class="[
        'flex w-full items-center gap-2 px-2.5 py-2 bg-gray-100 text-left transition-colors duration-200 hover:bg-gray-200',
        open ? 'rounded-t-md' : 'rounded-md'
      ]"
      @click="$emit('toggle')"
    >
      <slot name="header" />
      <svg
        width="12"
        height="12"
        viewBox="0 0 12 12"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="text-gray-400 shrink-0 transition-transform duration-200"
        :class="open ? 'rotate-180' : ''"
      >
        <path d="M2 4L6 8L10 4" />
      </svg>
    </button>
    <Transition name="accordion">
      <div v-if="open" :class="['border-t border-gray-100', bodyClass]">
        <slot />
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.accordion-enter-active,
.accordion-leave-active {
  transition:
    max-height 0.2s ease,
    opacity 0.2s ease;
  max-height: 800px;
  overflow: hidden;
}

.accordion-enter-from,
.accordion-leave-to {
  max-height: 0;
  opacity: 0;
}
</style>

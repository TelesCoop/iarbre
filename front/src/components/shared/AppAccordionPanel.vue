<script lang="ts" setup>
import { inject, computed } from "vue"

interface AccordionPanelProps {
  value: string
}

const props = defineProps<AccordionPanelProps>()

const accordion = inject<{
  toggleItem: (value: string) => void
  isActive: (value: string) => boolean
}>("accordion")

const isExpanded = computed(() => accordion?.isActive(props.value) ?? false)

const toggle = () => {
  accordion?.toggleItem(props.value)
}
</script>

<template>
  <div class="accordion-panel" :class="{ 'is-expanded': isExpanded }">
    <button type="button" class="accordion-header" :aria-expanded="isExpanded" @click="toggle">
      <slot name="header" />
      <svg
        class="accordion-icon"
        :class="{ rotated: isExpanded }"
        width="12"
        height="12"
        viewBox="0 0 12 12"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M2 4L6 8L10 4"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>
    </button>
    <Transition name="accordion-slide">
      <div v-if="isExpanded" class="accordion-content">
        <div class="accordion-content-inner">
          <slot />
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.accordion-panel {
  border-bottom: 1px solid #e5e7eb;
}

.accordion-panel:last-child {
  border-bottom: none;
}

.accordion-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 0.75rem 1rem;
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  text-align: left;
  transition: background-color 0.2s;
}

.accordion-header:hover {
  background-color: #f9fafb;
}

.accordion-icon {
  flex-shrink: 0;
  color: #9ca3af;
  transition: transform 0.2s ease;
}

.accordion-icon.rotated {
  transform: rotate(180deg);
}

.accordion-content {
  overflow: hidden;
}

.accordion-content-inner {
  padding: 0.75rem 1rem;
  background-color: #f9fafb;
}

.accordion-slide-enter-active,
.accordion-slide-leave-active {
  transition: all 0.2s ease;
}

.accordion-slide-enter-from,
.accordion-slide-leave-to {
  opacity: 0;
  max-height: 0;
}

.accordion-slide-enter-to,
.accordion-slide-leave-from {
  opacity: 1;
  max-height: 500px;
}
</style>

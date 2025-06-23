<script lang="ts" setup>
import { computed } from "vue"

interface Props {
  visible: boolean
  position?: "left" | "right" | "top" | "bottom"
  width?: string
  maxWidth?: string
  headerIcon?: string
  headerTitle?: string
}

interface Emits {
  (e: "update:visible", value: boolean): void
}

const props = withDefaults(defineProps<Props>(), {
  position: "left",
  width: "90%",
  maxWidth: "25rem",
  headerIcon: "",
  headerTitle: ""
})

const emit = defineEmits<Emits>()

const sidebarVisible = computed({
  get: () => props.visible,
  set: (value: boolean) => emit("update:visible", value)
})

const sidebarStyle = computed(() => ({
  width: props.width,
  "max-width": props.maxWidth
}))
</script>

<template>
  <Sidebar
    v-model:visible="sidebarVisible"
    :position="position"
    class="app-sidebar"
    :style="sidebarStyle"
  >
    <template #header>
      <slot name="header">
        <div v-if="headerIcon || headerTitle" class="flex items-center gap-2">
          <i v-if="headerIcon" :class="[headerIcon, 'text-xl']"></i>
          <span v-if="headerTitle" class="font-semibold text-lg">{{ headerTitle }}</span>
        </div>
      </slot>
    </template>

    <div class="sidebar-content">
      <slot></slot>
    </div>
  </Sidebar>
</template>

<style scoped>
.app-sidebar .sidebar-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
</style>

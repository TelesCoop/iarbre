<script lang="ts" setup>
import { computed } from "vue"

interface Props {
  visible: boolean
  position?: "left" | "right" | "top" | "bottom"
  customStyles?: {
    width?: string
    maxWidth?: string
    height?: string
  }
  headerIcon?: string
  headerTitle?: string
}

interface Emits {
  (e: "update:visible", value: boolean): void
}

const props = withDefaults(defineProps<Props>(), {
  position: "left",
  customStyles: () => ({}),
  headerIcon: "",
  headerTitle: ""
})

const drawerStyle = computed(() => {
  const defaultvalue = ["top", "bottom"].includes(props.position)
    ? { height: "auto", maxHeight: "90%" }
    : { width: "90%", maxWidth: "25rem" }

  return { ...defaultvalue, ...props.customStyles }
})
const emit = defineEmits<Emits>()

const drawerVisible = computed({
  get: () => props.visible,
  set: (value: boolean) => emit("update:visible", value)
})
</script>

<template>
  <Drawer
    v-model:visible="drawerVisible"
    :position="position"
    class="app-drawer"
    :style="drawerStyle"
    data-cy="app-drawer"
  >
    <template #header>
      <slot name="header">
        <div v-if="headerIcon || headerTitle" class="flex items-center gap-2">
          <i v-if="headerIcon" :class="[headerIcon, 'text-xl']"></i>
          <span v-if="headerTitle" class="font-semibold text-lg">{{ headerTitle }}</span>
        </div>
      </slot>
    </template>

    <div class="drawer-content" data-cy="drawer-content">
      <slot></slot>
    </div>
  </Drawer>
</template>

<style scoped>
.app-drawer .drawer-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
</style>

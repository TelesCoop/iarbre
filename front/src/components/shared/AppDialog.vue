<script lang="ts" setup>
import { computed, watch, onMounted, onUnmounted, ref } from "vue"

interface DialogProps {
  visible: boolean
  header?: string
  modal?: boolean
  draggable?: boolean
  closable?: boolean
  width?: string
  dataCy?: string
}

const props = withDefaults(defineProps<DialogProps>(), {
  header: "",
  modal: true,
  draggable: false,
  closable: true,
  width: "25rem",
  dataCy: undefined
})

const emit = defineEmits<{
  (e: "update:visible", value: boolean): void
  (e: "hide"): void
}>()

const dialogRef = ref<HTMLDialogElement | null>(null)

const isVisible = computed({
  get: () => props.visible,
  set: (value: boolean) => emit("update:visible", value)
})

const close = () => {
  isVisible.value = false
  emit("hide")
}

const handleBackdropClick = (event: MouseEvent) => {
  if (props.modal && event.target === dialogRef.value) {
    close()
  }
}

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === "Escape" && props.closable) {
    close()
  }
}

watch(
  () => props.visible,
  (newValue) => {
    if (newValue) {
      document.body.style.overflow = "hidden"
    } else {
      document.body.style.overflow = ""
    }
  }
)

onMounted(() => {
  document.addEventListener("keydown", handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener("keydown", handleKeydown)
  document.body.style.overflow = ""
})
</script>

<template>
  <Teleport to="body">
    <Transition name="dialog-fade">
      <div
        v-if="isVisible"
        ref="dialogRef"
        class="dialog-overlay"
        :class="{ 'dialog-modal': modal }"
        @click="handleBackdropClick"
      >
        <div
          class="dialog-container"
          :style="{ width }"
          role="dialog"
          aria-modal="true"
          :aria-labelledby="header ? 'dialog-header' : undefined"
          :data-cy="dataCy"
        >
          <div class="dialog-header">
            <h2 v-if="header" id="dialog-header" class="dialog-title">
              {{ header }}
            </h2>
            <slot name="header" />
            <button
              v-if="closable"
              type="button"
              class="dialog-close"
              aria-label="Fermer"
              @click="close"
            >
              <svg
                width="14"
                height="14"
                viewBox="0 0 14 14"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M1 1L13 13M1 13L13 1"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                />
              </svg>
            </button>
          </div>
          <div class="dialog-content">
            <slot />
          </div>
          <div v-if="$slots.footer" class="dialog-footer">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.dialog-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.dialog-modal {
  background-color: rgba(0, 0, 0, 0.4);
}

.dialog-container {
  background: white;
  border-radius: 0.75rem;
  box-shadow:
    0 20px 25px -5px rgba(0, 0, 0, 0.1),
    0 10px 10px -5px rgba(0, 0, 0, 0.04);
  max-height: 90vh;
  max-width: 90vw;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.dialog-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.dialog-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border: none;
  background: transparent;
  color: #6b7280;
  cursor: pointer;
  border-radius: 0.375rem;
  transition: all 0.2s;
}

.dialog-close:hover {
  background-color: #f3f4f6;
  color: #1f2937;
}

.dialog-content {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.dialog-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.dialog-fade-enter-active,
.dialog-fade-leave-active {
  transition: opacity 0.2s ease;
}

.dialog-fade-enter-active .dialog-container,
.dialog-fade-leave-active .dialog-container {
  transition: transform 0.2s ease;
}

.dialog-fade-enter-from,
.dialog-fade-leave-to {
  opacity: 0;
}

.dialog-fade-enter-from .dialog-container,
.dialog-fade-leave-to .dialog-container {
  transform: scale(0.95);
}
</style>

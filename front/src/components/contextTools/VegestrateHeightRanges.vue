<script lang="ts" setup>
import { computed, ref, watch } from "vue"
import { useDebounceFn } from "@vueuse/core"
import { useMapStore } from "@/stores/map"
import { normalizeHeightRanges, type HeightRange } from "@/utils/vegetation"

type RangeInput = { min: number | ""; max: number | "" }

const mapStore = useMapStore()

const toRows = (ranges: HeightRange[]): RangeInput[] =>
  ranges.map(({ min, max }) => ({ min, max: max === null ? "" : max }))

const rowError = ({ min, max }: RangeInput): string | null => {
  if (min === "" && max === "") return null
  if (min === "") return "Indiquez une hauteur minimale"
  if (min < 0) return "La hauteur doit être positive"
  if (max !== "" && max <= min) return "Le maximum doit dépasser le minimum"
  return null
}

const rows = ref<RangeInput[]>(toRows(mapStore.vegestrateHeightRanges))

const rowErrors = computed(() => rows.value.map(rowError))

const toRanges = (): HeightRange[] =>
  rows.value
    .filter((row) => row.min !== "" && !rowError(row))
    .map(({ min, max }) => ({ min: min as number, max: max === "" ? null : (max as number) }))

const sameRanges = (a: HeightRange[], b: HeightRange[]) =>
  a.length === b.length &&
  a.every((range, index) => range.min === b[index].min && range.max === b[index].max)

const apply = useDebounceFn(() => mapStore.setVegestrateHeightRanges(toRanges()), 200)

watch(
  () => mapStore.vegestrateHeightRanges,
  (ranges) => {
    if (!sameRanges(ranges, normalizeHeightRanges(toRanges()))) rows.value = toRows(ranges)
  }
)

const addRow = () => {
  rows.value.push({ min: "", max: "" })
}

const removeRow = (index: number) => {
  rows.value.splice(index, 1)
  apply()
}

const reset = () => {
  rows.value = []
  mapStore.setVegestrateHeightRanges([])
}
</script>

<template>
  <div class="flex flex-col gap-2" data-cy="vegestrate-height-ranges">
    <div class="flex items-center justify-between gap-2">
      <span class="text-xs font-sans font-medium text-gray-700">Plages de hauteur</span>
      <button
        v-if="rows.length"
        type="button"
        class="text-xs font-sans text-primary-600 underline cursor-pointer border-0 bg-transparent p-0"
        @click="reset"
      >
        Tout afficher
      </button>
    </div>

    <div v-for="(row, index) in rows" :key="index" class="flex flex-col gap-0.5">
      <div class="flex items-center gap-1">
        <input
          v-model.number="row.min"
          type="number"
          min="0"
          step="1"
          placeholder="min"
          :aria-label="`Hauteur minimale de la plage ${index + 1}`"
          :aria-invalid="Boolean(rowErrors[index])"
          :class="['height-range-input', rowErrors[index] ? 'border-red-400' : '']"
          @input="apply"
        />
        <span class="height-range-unit">–</span>
        <input
          v-model.number="row.max"
          type="number"
          min="0"
          step="1"
          placeholder="∞"
          :aria-label="`Hauteur maximale de la plage ${index + 1}`"
          :aria-invalid="Boolean(rowErrors[index])"
          :class="['height-range-input', rowErrors[index] ? 'border-red-400' : '']"
          @input="apply"
        />
        <span class="height-range-unit">m</span>
        <button
          type="button"
          class="ml-auto flex h-5 w-5 items-center justify-center rounded-full border-0 bg-transparent text-base leading-none text-gray-400 cursor-pointer transition-colors duration-150 hover:bg-gray-100 hover:text-gray-700"
          :aria-label="`Supprimer la plage ${index + 1}`"
          @click="removeRow(index)"
        >
          ×
        </button>
      </div>
      <span v-if="rowErrors[index]" role="alert" class="text-xs font-sans text-red-600">{{
        rowErrors[index]
      }}</span>
    </div>

    <button type="button" class="layer-chip self-start" @click="addRow">+ Ajouter une plage</button>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.height-range-input {
  @apply w-14 rounded-md border border-gray-200 px-2 py-1;
  @apply text-xs font-sans text-gray-800;
  @apply focus:outline-none focus:ring-2 focus:ring-primary-200;
}

.height-range-unit {
  @apply text-xs font-sans text-gray-500;
}
</style>

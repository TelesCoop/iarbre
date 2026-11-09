<script lang="ts" setup>
import { computed, ref } from "vue"
import { useMapStore } from "@/stores/map"
import { DataTypeToLabel } from "@/utils/enum"
import { HOURLY_RASTERS } from "@/utils/hourlyRaster"

const mapStore = useMapStore()

const raster = computed(() => HOURLY_RASTERS[mapStore.selectedDataType]!)

const title = computed(() =>
  [
    DataTypeToLabel[mapStore.selectedDataType],
    ...(raster.value.years ? [mapStore.rasterYear] : [])
  ].join(" - ")
)

const scale = ref<HTMLElement | null>(null)
const description = ref<HTMLDetailsElement | null>(null)

const onDescriptionToggle = () => {
  const target = description.value?.open ? description.value : scale.value
  target?.scrollIntoView({ behavior: "smooth", block: "start" })
}
</script>

<template>
  <div class="flex flex-col flex-1 min-h-0 gap-3 px-2 py-3 md:py-4 overflow-y-auto">
    <div
      ref="scale"
      class="flex flex-col gap-1 bg-white border border-gray-200 rounded-lg p-3"
      data-cy="hourly-raster-scale"
    >
      <h3 class="text-sm font-bold text-primary-900">{{ title }}</h3>
      <table class="w-full text-sm text-gray-700">
        <thead>
          <tr class="text-primary-900">
            <th class="pb-1 text-left align-bottom font-bold" colspan="2">
              {{ raster.columnLabels[0] }}
            </th>
            <th class="pb-1 pl-2 text-left align-bottom font-bold">
              {{ raster.columnLabels[1] }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in raster.classes" :key="item.value" class="border-t border-gray-100">
            <td class="w-4 py-1">
              <span
                :style="{ backgroundColor: item.color }"
                aria-hidden="true"
                class="block w-4 h-4 rounded-sm border border-gray-300"
              ></span>
            </td>
            <td class="py-1 pl-2">{{ item.label }}</td>
            <td class="py-1 pl-2">{{ item.detail }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <details
      ref="description"
      class="bg-white border border-gray-200 rounded-lg p-3"
      data-cy="hourly-raster-description"
      @toggle="onDescriptionToggle"
    >
      <summary class="text-sm font-bold text-primary-900 cursor-pointer">
        {{ raster.descriptionSummary }}
      </summary>
      <div class="flex flex-col gap-2 mt-2 text-sm text-gray-700">
        <slot />
      </div>
    </details>
  </div>
</template>

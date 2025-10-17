<script lang="ts" setup>
import type { City } from "@/types/division"
import DivisionDataDisplay from "./DivisionDataDisplay.vue"

interface CityCardProps {
  city: City
}

const props = defineProps<CityCardProps>()
</script>

<template>
  <DivisionDataDisplay :data="city" />
</template>

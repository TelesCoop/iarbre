<script lang="ts" setup>
import type { Iris } from "@/types/division"
import DivisionDataDisplay from "./DivisionDataDisplay.vue"

interface IrisCardProps {
  iris: Iris
}

const props = defineProps<IrisCardProps>()
</script>

<template>
  <DivisionDataDisplay :data="iris" />
</template>

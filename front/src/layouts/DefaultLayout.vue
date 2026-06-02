<script lang="ts" setup>
import FeedbackBanner from "@/components/FeedbackBanner.vue"
</script>

<template>
  <div class="flex flex-col min-h-screen">
    <FeedbackBanner />
    <main class="flex-1">
      <slot></slot>
    </main>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";
</style>

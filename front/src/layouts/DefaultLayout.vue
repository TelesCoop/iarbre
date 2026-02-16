<script lang="ts" setup></script>

<template>
  <div class="flex flex-col min-h-screen">
    <main class="flex-1">
      <slot></slot>
    </main>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";
</style>

<script lang="ts" setup>
import Navbar from "@/components/navbar/NavbarComponent.vue"
</script>

<template>
  <div class="flex flex-col min-h-screen">
    <header class="navbar shadow-lg" data-cy="navbar">
      <Navbar />
    </header>
    <main class="flex-1">
      <slot></slot>
    </main>
  </div>
</template>

<style scoped>
.navbar {
  @apply flex items-center justify-between;
  height: calc(var(--header-height));
  padding: 30px 15px 30px 30px;
}
</style>

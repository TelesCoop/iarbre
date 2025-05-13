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
@reference "@/styles/main.css";

.navbar {
  @apply flex items-center justify-between;
  @apply z-1;
  height: calc(var(--header-height));
  @apply p-4;
}

@screen sm {
  .navbar {
    @apply p-[30px_15px_30px_30px];
  }
}
</style>

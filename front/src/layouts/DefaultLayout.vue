<script setup lang="ts">
import Navbar from "@/components/NavbarComponent.vue"
</script>

<template>
  <div class="flex flex-col min-h-screen">
    <header
      class="navbar fixed w-full top-0 z-10 flex items-center justify-between px-10 py-2.5 bg-[var(--color-off-white)]"
      data-cy="navbar"
    >
      <Navbar />
    </header>
    <main class="flex-1 mt-20">
      <slot></slot>
    </main>
  </div>
</template>

<style scoped>
.navbar {
  height: var(--header-height);
  box-sizing: border-box;
  overflow: hidden;
}
</style>

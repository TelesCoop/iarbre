<script setup lang="ts">
import Navbar from "@/components/NavbarComponent.vue"
</script>

<template>
  <div class="layout">
    <header class="navbar">
      <Navbar />
    </header>
    <main class="default-content">
      <slot></slot>
    </main>
  </div>
</template>

<style scoped lang="sass">
.layout
  display: flex
  flex-direction: column
  min-height: 100vh

.default-content
  min-height: $content-height
  margin-top: $header-height
  flex: 1
</style>

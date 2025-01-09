<script setup lang="ts"></script>

<template>
  <div>
    <header class="default-header">
      <div>Header</div>
    </header>
    <main class="default-content">
      <slot></slot>
    </main>
    <footer class="default-footer">
      <div>footer</div>
    </footer>
  </div>
</template>

<style scoped lang="sass">

.default-header
  box-sizing: border-box
  height: $header-height

.default-content
  min-height: $content-height

.default-footer
  box-sizing: border-box
  height: $footer-height
</style>

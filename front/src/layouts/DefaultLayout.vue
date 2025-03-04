<script setup lang="ts">
import { useFeedbackStore } from "@/stores/feedback"
const store = useFeedbackStore()
</script>

<template>
  <div class="layout">
    <header class="navbar">
      <div class="navbar-left">
        <a href="/">
          <img class="navbar-logo" src="/images/logo-iarbre.png" alt="Logo I-Arbre" />
        </a>
      </div>
      <nav class="navbar-right">
        <ul>
          <li>
            <a href="#" class="navbar-link" @click.prevent="store.showFeedback"
              >✉️ Nous envoyer votre retour</a
            >
          </li>
          <li><a href="https://iarbre.fr" class="navbar-link">ⓘ En savoir plus</a></li>
        </ul>
      </nav>
    </header>
    <main class="default-content">
      <slot></slot>
    </main>
  </div>
</template>

<style scoped lang="sass">
.navbar
  background-color: $off-white
  height: $header-height
  position: fixed
  width: 100%
  top: 0
  z-index: 2
  box-sizing: border-box
  overflow: hidden

  display: flex
  align-items: center
  justify-content: space-between
  padding: 10px 40px

  .navbar-logo
    height: 40px
    width: auto

  .navbar-right
    ul
      list-style: none
      display: flex
      gap: 1.1rem
      flex-direction: horizontal

  .navbar-link
    font-family: $accent-font, Arial, sans-serif
    color: $brown
    text-decoration: none
    font-size: 1rem
    transition: color 0.3s ease

    &:hover
      color: $light-green


.layout
  display: flex
  flex-direction: column
  min-height: 100vh

.default-content
  min-height: $content-height
  margin-top: $header-height
  flex: 1
</style>

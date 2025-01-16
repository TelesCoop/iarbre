<script setup lang="ts"></script>

<template>
  <div class="layout">
    <header class="default-header">
      <div class="header-content">
        <div class="logo">
          <h1>IA.rbre</h1>
        </div>
        <nav class="main-nav">
          <router-link to="/" class="nav-link">Home</router-link>
          <a href="mailto:contact@telescoop.fr" class="nav-link">Contact</a>
        </nav>
      </div>
    </header>

    <main class="default-content">
      <slot></slot>
    </main>

    <footer class="default-footer">
      <div class="footer-content">
        <div class="footer-section">
          <h3>Contactez nous</h3>
          <p>Email: contact@telescoop.fr</p>
        </div>
        <div class="footer-section">
          <h3>Suivez nous</h3>
          <div class="social-links">
            <a
              href="https://www.linkedin.com/company/telescoop-fr/posts/?feedView=all"
              class="social-link"
              >LinkedIn</a
            >
          </div>
        </div>
      </div>
      <div class="footer-bottom">
        <p>© 2024 Telescoop. Tous droits réservés.</p>
      </div>
    </footer>
  </div>
</template>

<style scoped lang="sass">
.layout
  display: flex
  flex-direction: column
  min-height: 100vh

.default-header
  box-sizing: border-box
  height: $header-height
  background-color: #ffffff
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1)
  position: fixed
  width: 100%
  top: 0
  z-index: 1000

  .header-content
    max-width: 1200px
    margin: 0 auto
    padding: 0 20px
    display: flex
    justify-content: space-between
    align-items: center
    height: 100%

  .logo
    h1
      margin: 0
      font-size: 24px

  .main-nav
    display: flex
    gap: 20px

    .nav-link
      text-decoration: none
      color: #333
      padding: 8px 12px
      border-radius: 4px
      transition: background-color 0.3s

      &:hover
        background-color: #f5f5f5

.default-content
  min-height: $content-height
  margin-top: $header-height
  flex: 1
  padding: 20px

.default-footer
  box-sizing: border-box
  height: auto
  min-height: $footer-height
  background-color: #2c3e50
  color: #ffffff
  padding: 40px 0 20px

  .footer-content
    max-width: 1200px
    margin: 0 auto
    padding: 0 20px
    display: grid
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr))
    gap: 40px

  .footer-section
    h3
      margin: 0 0 15px 0
      font-size: 18px

    a
      display: block
      color: #ffffff
      text-decoration: none
      margin-bottom: 10px
      opacity: 0.8

      &:hover
        opacity: 1

  .social-links
    display: flex
    gap: 15px

  .footer-bottom
    margin-top: 40px
    padding-top: 20px
    border-top: 1px solid rgba(255, 255, 255, 0.1)
    text-align: center

    p
      margin: 0
      opacity: 0.8

@media (max-width: 768px)
  .default-header
    .header-content
      flex-direction: column
      padding: 10px
      gap: 10px

  .default-footer
    .footer-content
      grid-template-columns: 1fr
      gap: 30px
</style>

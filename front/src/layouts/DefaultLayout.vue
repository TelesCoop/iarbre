<script setup lang="ts"></script>

<template>
  <div class="layout">
    <header class="navbar">
      <div class="navbar-left">
        <img class="navbar-logo" src="/images/logo-iarbre.png" alt="Logo I-Arbre" />
      </div>
      <nav class="navbar-right">
        <ul>
          <li><a href="mailto:contact@telescoop.fr" class="nav-link">Contact</a></li>
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
  padding: 10px

  .navbar-logo
    height: 40px
    width: auto

  .navbar-right
    ul
      list-style: none
      display: flex
      flex-direction: horizontal
// .layout
//   display: flex
//   flex-direction: column
//   min-height: 100vh

// .default-header
//   background-color: #ffffff
//   box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1)

//   .header-content
//     max-width: 1200px
//     margin: 0 auto
//     padding: 0 20px
//     display: flex
//     justify-content: space-between
//     align-items: center
//     height: 100%

//   .logo
//     h1
//       margin: 0
//       font-size: 24px

//   .main-nav
//     display: flex
//     gap: 20px

//     .nav-link
//       text-decoration: none
//       color: #333
//       padding: 8px 12px
//       border-radius: 4px
//       transition: background-color 0.3s

//       &:hover
//         background-color: #f5f5f5

.default-content
  min-height: $content-height
  margin-top: $header-height
  flex: 1

// .default-footer
//   box-sizing: border-box
//   height: auto
//   min-height: $footer-height
//   background-color: #2c3e50
//   color: #ffffff
//   padding: 40px 0 20px

//   .footer-content
//     max-width: 1200px
//     margin: 0 auto
//     padding: 0 20px
//     display: grid
//     grid-template-columns: repeat(auto-fit, minmax(250px, 1fr))
//     gap: 40px

//   .footer-section
//     h3
//       margin: 0 0 15px 0
//       font-size: 18px

//     a
//       display: block
//       color: #ffffff
//       text-decoration: none
//       margin-bottom: 10px
//       opacity: 0.8

//       &:hover
//         opacity: 1

//   .social-links
//     display: flex
//     gap: 15px

//   .footer-bottom
//     margin-top: 40px
//     padding-top: 20px
//     border-top: 1px solid rgba(255, 255, 255, 0.1)
//     text-align: center

//     p
//       margin: 0
//       opacity: 0.8

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

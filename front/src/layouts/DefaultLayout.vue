<script setup lang="ts"></script>

<template>
  <div class="flex flex-col min-h-screen">
    <header
      class="navbar fixed w-full top-0 z-10 flex items-center justify-between px-10 py-2.5 bg-[var(--color-off-white)]"
    >
      <div>
        <a href="/">
          <img class="h-10 w-auto" src="/images/logo-iarbre.png" alt="Logo I-Arbre" />
        </a>
      </div>
      <nav>
        <ul class="flex">
          <li>
            <a
              href="https://iarbre.fr"
              class="font-[var(--font-accent)] text-[var(--color-brown)] no-underline hover:text-[var(--color-light-green)] transition-colors duration-300"
              >ⓘ En savoir plus</a
            >
          </li>
        </ul>
      </nav>
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

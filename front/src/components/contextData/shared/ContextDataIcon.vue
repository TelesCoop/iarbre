<script lang="ts" setup>
withDefaults(
  defineProps<{
    name?: string
    size?: number
  }>(),
  {
    name: "generic",
    size: 16
  }
)
</script>

<template>
  <svg
    :width="size"
    :height="size"
    aria-hidden="true"
    fill="none"
    stroke="currentColor"
    stroke-linecap="round"
    stroke-linejoin="round"
    stroke-width="2"
    viewBox="0 0 24 24"
  >
    <template v-if="name === 'tree'">
      <path d="M12 22v-7" />
      <path d="M7 15h10l-5-12z" />
    </template>
    <template v-else-if="name === 'sun'">
      <circle cx="12" cy="12" r="4" />
      <path
        d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"
      />
    </template>
    <template v-else-if="name === 'moon'">
      <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" />
    </template>
    <template v-else-if="name === 'building'">
      <rect height="20" rx="2" width="16" x="4" y="2" />
      <path
        d="M9 22v-4h6v4M8 6h.01M12 6h.01M16 6h.01M8 10h.01M12 10h.01M16 10h.01M8 14h.01M12 14h.01M16 14h.01"
      />
    </template>
    <template v-else-if="name === 'road'">
      <path d="M9 18l2-12M13 6l2 12M5 22l5-20M14 2l5 20" />
      <path d="M12 8v2M12 14v2" />
    </template>
    <template v-else-if="name === 'vegetation'">
      <path d="M5 21c8 0 14-6 14-14V3h-4C7 3 3 7 3 15c0 2 1 4 2 6Z" />
      <path d="M3 21c4-4 8-8 16-12" />
    </template>
    <template v-else-if="name === 'water'">
      <path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11Z" />
    </template>
    <template v-else-if="name === 'network'">
      <circle cx="6" cy="6" r="2" />
      <circle cx="18" cy="6" r="2" />
      <circle cx="12" cy="18" r="2" />
      <path d="M8 7l3 8M16 7l-3 8M8 6h8" />
    </template>
    <template v-else-if="name === 'transport'">
      <path d="M6 17h12l1-5-2-6H7l-2 6 1 5Z" />
      <path d="M8 17v2M16 17v2M7 12h10" />
      <circle cx="8" cy="15" r="1" />
      <circle cx="16" cy="15" r="1" />
    </template>
    <template v-else-if="name === 'heat'">
      <path d="M14 14.76V5a2 2 0 0 0-4 0v9.76a4 4 0 1 0 4 0Z" />
    </template>
    <template v-else-if="name === 'capacity'">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z" />
      <path d="M9 12l2 2 4-4" />
    </template>
    <template v-else-if="name === 'people'">
      <path d="M16 21v-2a4 4 0 0 0-8 0v2" />
      <circle cx="12" cy="7" r="4" />
      <path d="M22 21v-2a4 4 0 0 0-3-3.87M2 21v-2a4 4 0 0 1 3-3.87" />
    </template>
    <template v-else-if="name === 'tool'">
      <path d="M14.7 6.3a4 4 0 0 0-5 5L3 18v3h3l6.7-6.7a4 4 0 0 0 5-5l-2.4 2.4-2-2 2.4-2.4Z" />
    </template>
    <template v-else>
      <circle cx="12" cy="12" r="8" />
      <path d="M12 8v4l3 2" />
    </template>
  </svg>
</template>

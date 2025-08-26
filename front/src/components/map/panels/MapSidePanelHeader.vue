<template>
  <div
    class="bg-primary-500 shadow-md"
    style="
      display: flex;
      height: 10.25rem;
      padding: 1.0625rem 1.25rem 2.1875rem 1.25rem;
      flex-direction: column;
      align-items: flex-start;
      gap: 0.625rem;
      flex-shrink: 0;
      align-self: stretch;
    "
  >
    <h2 class="text-lg text-white font-semibold font-accent">🏙️ Agglomération de Lyon</h2>
    <div class="flex gap-2 flex-row items-start self-stretch">
      <div class="stat-card bg-primary-200 text-white px-3 py-2 text-sm text-center font-medium==">
        1.44M<br /><span style="font-size: 0.75rem">habitants</span>
      </div>
      <div class="stat-card bg-primary-200 text-white px-3 py-2 text-sm text-center font-medium">
        240 km²<br /><span style="font-size: 0.75rem">superficie</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stat-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 1.5625rem;
  align-self: stretch;
  height: 4.5625rem;
  border-radius: 0.375rem;
}
</style>

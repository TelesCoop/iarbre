<script setup lang="ts">
defineProps({
  score: {
    required: true,
    type: Number
  },
  label: {
    required: true,
    type: String
  },
  size: {
    required: true,
    type: String
  }
})
</script>

<template>
  <div
    class="hexagon relative m-[5px] block text-center"
    :class="{ [`scale-${score}`]: true, [size]: true }"
  >
    <span>{{ label }}</span>
  </div>
</template>

<style scoped>
/* Base hexagon styles */
.hexagon {
  font-family: var(--font-accent);
  position: relative;
}

.hexagon::before,
.hexagon::after {
  content: "";
  position: absolute;
  width: 0;
  left: 0;
}

.hexagon::before {
  bottom: 100%;
}

.hexagon::after {
  top: 100%;
}

/* Small hexagon */
.hexagon.small {
  height: calc(1.732 * 12px); /* sqrt(3) * 12px */
  width: calc(3 * 12px);
  margin-top: calc(12px + 5px);
  margin-bottom: calc(12px + 5px);
  font-size: 1.3rem;
}

.hexagon.small::before {
  border-left: calc(1.5 * 12px) solid transparent;
  border-right: calc(1.5 * 12px) solid transparent;
  border-bottom: calc(1.732 / 2 * 12px) solid transparent;
}

.hexagon.small::after {
  border-left: calc(1.5 * 12px) solid transparent;
  border-right: calc(1.5 * 12px) solid transparent;
  border-top: calc(1.732 / 2 * 12px) solid transparent;
}

/* Huge hexagon */
.hexagon.huge {
  height: calc(1.732 * 20px); /* sqrt(3) * 20px */
  width: calc(3 * 20px);
  margin-top: calc(20px + 5px);
  margin-bottom: calc(20px + 5px);
  font-size: 1.2rem;
  line-height: 2.3rem;
}

.hexagon.huge::before {
  border-left: calc(1.5 * 20px) solid transparent;
  border-right: calc(1.5 * 20px) solid transparent;
  border-bottom: calc(1.732 / 2 * 20px) solid transparent;
}

.hexagon.huge::after {
  border-left: calc(1.5 * 20px) solid transparent;
  border-right: calc(1.5 * 20px) solid transparent;
  border-top: calc(1.732 / 2 * 20px) solid transparent;
}

/* Scale colors - using postcss-for */
@for $i from 0 to 7 {
  .hexagon.scale-$(i) {
    background-color: var(--color-scale-$(i));
    color: var(--color-brown);
  }
  .hexagon.scale-$(i)::before {
    border-bottom-color: var(--color-scale-$(i));
  }
  .hexagon.scale-$(i)::after {
    border-top-color: var(--color-scale-$(i));
  }
}

@for $i from 7 to 11 {
  .hexagon.scale-$(i) {
    background-color: var(--color-scale-$(i));
    color: var(--color-white);
  }
  .hexagon.scale-$(i)::before {
    border-bottom-color: var(--color-scale-$(i));
  }
  .hexagon.scale-$(i)::after {
    border-top-color: var(--color-scale-$(i));
  }
}
</style>

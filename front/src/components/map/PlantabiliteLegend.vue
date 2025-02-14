<template>
  <div class="plantabilite-legend">
    <span class="plantabilite-legend-text">Non plantable</span>
    <div class="is-flex">
      <div
        v-for="index in [0, 2, 4, 6, 8, 10]"
        :key="index"
        class="plantabilite-legend-scale hexagon"
        :class="{ ['scale-' + index]: true }"
      >
        <span>{{ index }}</span>
      </div>
    </div>
    <span class="plantabilite-legend-text">Plantable</span>
  </div>
</template>

<style lang="sass" scoped>

$hexagon-width: 12px


.plantabilite-legend
  font-family: $accent-font
  display: flex
  align-items: center
  justify-content: center
  line-height: 0.75rem // 12px
  font-size: 0.75rem // 12px
  gap: 8px

  .is-flex
    display: flex
    padding: 0.5rem

  .plantabilite-legend-scale
    display: flex
    align-items: center
    justify-content: center
    width: 25px
    height: 20px
    color: white
    font-size: 1.3em

  .hexagon
    &.scale-0
      background-color: $scale-0
      color: $brown
      &::before
        border-bottom-color: $scale-0
      &::after
        border-top-color: $scale-0
    &.scale-2
      background-color: $scale-2
      color: $brown
      &::before
        border-bottom-color: $scale-2
      &::after
        border-top-color: $scale-2

    &.scale-4
      background-color: $scale-4
      color: $brown
      &::before
        border-bottom-color: $scale-4
      &::after
        border-top-color: $scale-4

    &.scale-6
      color: $brown
      background-color: $scale-6
      &::before
        border-bottom-color: $scale-6
      &::after
        border-top-color: $scale-6

    &.scale-8
      color: $brown
      background-color: $scale-8
      &::before
        border-bottom-color: $scale-8
      &::after
        border-top-color: $scale-8

    &.scale-10
      background-color: $scale-10
      &::before
        border-bottom-color: $scale-10
      &::after
        border-top-color: $scale-10

    position: relative
    height: calc(sqrt(3) * $hexagon-width)
    width: calc(3 * $hexagon-width)
    margin: 5px

    &::before
      content: ""
      position: absolute
      width: 0
      border-left: calc(1.5 * $hexagon-width) solid transparent
      border-right: calc(1.5 * $hexagon-width) solid transparent
      bottom: 100%
      border-bottom: calc(sqrt(3) / 2 * $hexagon-width) solid red

    &::after
      content: ""
      position: absolute
      width: 0
      border-left: calc(1.5 * $hexagon-width) solid transparent
      border-right: calc(1.5 * $hexagon-width) solid transparent
      top: 100%
      width: 0
      border-top: calc(sqrt(3) / 2 * $hexagon-width) solid #007BFF

  .plantabilite-legend-text
    font-size: 0.9rem
    line-height: 0.75rem
</style>

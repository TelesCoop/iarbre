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
  <div class="hexagon" :class="{ [`scale-${score}`]: true, [size]: true }">
    <span>{{ label }}</span>
  </div>
</template>

<style lang="sass" scoped>

$hexagons-width: ("small": 12px, "huge": 20px)

.hexagon
    @each $name, $hexagon-width in $hexagons-width
        &.#{$name}
            height: calc(sqrt(3) * $hexagon-width)
            width: calc(3 * $hexagon-width)
            margin-top: calc($hexagon-width + 5px)
            margin-bottom: calc($hexagon-width + 5px)

            &::before
                border-left: calc(1.5 * $hexagon-width) solid transparent
                border-right: calc(1.5 * $hexagon-width) solid transparent
                border-bottom: calc(sqrt(3) / 2 * $hexagon-width) solid red

            &::after
                border-left: calc(1.5 * $hexagon-width) solid transparent
                border-right: calc(1.5 * $hexagon-width) solid transparent
                border-top: calc(sqrt(3) / 2 * $hexagon-width) solid #007BFF

    @each $index, $color in $scales
        &.scale-#{$index}
            background-color: $color

            color: if(abs(lightness($color) - lightness($white)) < 40, $brown, $white)
            &::before
                border-bottom-color: $color
            &::after
                border-top-color: $color

    position: relative
    margin: 5px
    display: block
    text-align: center
    font-family: $accent-font

    &::before
        content: ""
        position: absolute
        width: 0
        bottom: 100%
        left: 0

    &::after
        content: ""
        position: absolute
        left: 0
        top: 100%
        width: 0

    &.huge
        font-size: 1.2rem
        line-height: 2.3rem

    &.small
        font-size: 1.3rem
</style>

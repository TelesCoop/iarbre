<script setup lang="ts">
const props = defineProps({
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
        color: $white
        &::before
            border-bottom-color: $scale-10
        &::after
            border-top-color: $scale-10

    position: relative
    margin: 5px
    display: block
    text-align: center

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
        font-size: 1.6rem
        line-height: 2.3rem

    &.small
        font-size: 1.3rem
</style>

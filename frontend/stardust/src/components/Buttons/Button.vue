<script setup lang="ts">
import { defineProps, computed } from 'vue'

const props = defineProps<{
  text?: string
  size?: string
  leftIcon?: string
  rightIcon?: string
  bgColor?: string
  isActiveButton?: boolean
}>()

const btnClass = computed(() => {
  const size = props.size || 'md'
  const bgColor = props.bgColor || 'bg-bg-secondary'
  const isActiveButton = props.isActiveButton
    ? 'bg-main-accent-hover hover:bg-main-accent-hover'
    : ''
  return `w-auto max-w-[400px] h-[35px] px-4 py-2 rounded-sm border border-border-primary ${bgColor} ${isActiveButton} hover:scale-105 transition-transform duration-300 flex items-center justify-center cursor-pointer text-text-primary`
})
</script>

<template>
  <div :class="btnClass">
    <slot>{{ props.text || 'Button' }}</slot>
  </div>
</template>

<style scoped></style>

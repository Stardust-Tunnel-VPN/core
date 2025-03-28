<script setup lang="ts">
import { defineProps, computed } from 'vue'

const props = defineProps<{
  name: string
  size?: 'small' | 'medium' | 'large'
  focused?: boolean
}>()

const sizeClassMap = {
  small: 'text-sm',
  medium: 'text-base',
  large: 'text-2xl',
}

const iconClasses = computed(() => [
  sizeClassMap[props.size || 'medium'],
  { 'cursor-pointer hover:scale-125 transition-transform duration-300': props.focused },
])
</script>

<template>
  <i class="material-icons" :class="iconClasses">
    {{ props.name }}
  </i>
</template>

<style scoped></style>

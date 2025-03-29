<script setup lang="ts">
import { defineProps, computed } from 'vue'

const props = defineProps<{
  name: string
  size?: 'small' | 'medium' | 'large'
  focused?: boolean
  variant?: 'filled' | 'outlined' | 'rounded' | 'sharp' | 'two-tone'
}>()

const sizeClassMap = {
  small: 'text-sm',
  medium: 'text-base',
  large: 'text-2xl',
}

const variantClassMap = {
  filled: 'material-icons',
  outlined: 'material-symbols-outlined',
  rounded: 'material-symbols-rounded',
  sharp: 'material-symbols-sharp',
  'two-tone': 'material-symbols-two-tone',
}

const iconClasses = computed(() => [
  variantClassMap[props.variant || 'filled'],
  sizeClassMap[props.size || 'medium'],
  { 'cursor-pointer hover:scale-125 transition-transform duration-300': props.focused },
])
</script>

<template>
  <i :class="iconClasses">
    {{ props.name }}
  </i>
</template>

<style scoped></style>

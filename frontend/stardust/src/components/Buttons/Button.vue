<script setup lang="ts">
import { defineProps } from 'vue'

const props = defineProps<{
  text: string
  size?: string
  leftIcon?: string
  rightIcon?: string
  bgColor?: string
}>()
</script>

<template>
  <div
    class="w-auto max-w-[400px] h-[35px] px-4 py-2 rounded-sm border border-border-primary bg-bg-secondary hover:bg-bg-hover hover:scale-105 transition-transform duration-300 flex items-center justify-center cursor-pointer"
  >
    <span class="text-text-primary">{{ props.text }}</span>
  </div>
</template>

<style scoped></style>

<script setup lang="ts">
import { defineProps, computed } from 'vue'
import { FRAME_SIZE_CLASSES, FRAME_BG_CLASSES } from '@/utils/enums/frame_sizes'

const props = defineProps<{
  size: 'small' | 'medium' | 'large' | 'table'
  headerText?: string
  subheaderText?: string
  isDarkMode?: boolean
  bgColor?: 'white' | 'gray'
}>()

const frameClasses = computed(() => {
  return [FRAME_SIZE_CLASSES[props.size]]
})

const showHeader = computed(() => props.headerText && props.subheaderText)
</script>

<template>
  <div
    :class="frameClasses"
    class="bg-bg-primary rounded-xl shadow-md transition-transform duration-300"
  >
    <div v-if="showHeader" class="flex flex-col items-start justify-between px-6 py-4">
      <h1 class="text-lg font-bold text-text-primary">{{ props.headerText }}</h1>
      <h2 class="text-sm text-text-secondary">{{ props.subheaderText }}</h2>
    </div>
    <slot />
  </div>
</template>

<style scoped></style>

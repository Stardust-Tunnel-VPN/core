<script setup lang="ts">
import { defineProps, computed } from 'vue'

const props = defineProps<{
  size: 'small' | 'medium' | 'large' | 'table'
  headerText?: string
  subheaderText?: string
  isDarkMode?: boolean
  bgColor?: 'white' | 'gray'
}>()

const frameSizeComputed = computed(() => {
  switch (props.size) {
    case 'small':
      return ['w-[125px]', 'h-[20px]']
    case 'medium':
      return ['w-[150px]', 'h-[25px]']
    case 'large':
      return ['w-[175px]', 'h-[30px]']
    case 'table':
      return ['w-[750px]', 'h-[450px]']
  }
})

const showHeader = computed(() => props.headerText && props.subheaderText)
</script>

<template>
  <div :class="frameSizeComputed" class="bg-white rounded-s-sm border-[1px] border-gray-300">
    <div v-if="showHeader" class="flex flex-col items-start justify-between px-4 py-2">
      <h1 class="text-lg font-bold">{{ props.headerText }}</h1>
      <h2 class="text-sm text-gray-200">{{ props.subheaderText }}</h2>
    </div>
    <slot />
  </div>
</template>

<style scoped></style>

<script setup lang="ts">
import { defineProps } from 'vue'
import Icon from '@/components/Icon.vue'

const props = defineProps<{
  text: string
  size?: string
  leftIcon?: string
  rightIcon?: string
  bgColor?: string
}>()
</script>

<template>
  <!-- TODO: make dynamic bg-color -->
  <div
    class="bg-white w-auto max-w-[400px] h-[35px] px-4 py-2 rounded-sm border-[1px] border-gray-300 hover:bg-gray-200 hover:scale-105 transition-transform duration-300 flex items-center justify-center cursor-pointer"
  >
    <!-- <Icon v-if="props.leftIcon" /> -->
    <!-- TODO: make the text in other font (not so thin) -->
    <!-- TODO: I still don't know what logic I'm about to provide here -->
    <span class="text-md">{{ props.text }}</span>
    <!-- <Icon v-if="props.rightIcon" /> -->
  </div>
</template>

<style scoped></style>

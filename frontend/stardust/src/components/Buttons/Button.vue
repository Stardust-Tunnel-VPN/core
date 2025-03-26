<script setup lang="ts">
import { defineProps } from 'vue'
import Icon from '@/components/Icon.vue'

const props = defineProps<{
  text: string
  size: string
  leftIcon?: string
  rightIcon?: string
  bgColor?: string
}>()
</script>

<template>
  <!-- TODO: make dynamic bg-color -->
  <div
    class="bg-white w-[125px] h-[20px] px-4 py-2 rounded-s-sm border-[1px] border-gray-300 hover:bg-gray-200 hover:scale-105 transition-transform duration-300"
  >
    <Icon v-if="props.leftIcon" />
    <span>{{ props.text }}</span>
    <Icon v-if="props.rightIcon" />
  </div>
</template>

<style scoped></style>

<script setup lang="ts">
import { defineProps, computed } from 'vue'
import Icon from '@/components/Icon.vue'

const props = defineProps<{
  text: string
  size?: string
  leftIcon?: string
  rightIcon?: string
}>()

// TODO - do it later based on connected-store

const isConnected = computed(() => {
  return props.text === 'Disconnect'
})

const bgColor = computed(() => {
  return isConnected.value ? 'bg-connected' : 'bg-disconnected'
})
</script>

<template>
  <div
    :class="bgColor"
    class="w-full max-w-[150px] h-[35px] px-4 py-2 rounded-sm border border-border-primary hover:scale-105 transition-transform duration-300 flex items-center justify-center cursor-pointer"
  >
    <span class="text-text-primary">{{ props.text }}</span>
  </div>
</template>

<style scoped></style>

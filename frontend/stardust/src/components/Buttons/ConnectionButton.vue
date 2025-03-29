<script setup lang="ts">
import { defineProps, computed } from 'vue'
import Icon from '@/components/Icon.vue'

// TODO - do it later based on connected-store

// based on the store state of course
const isConnected = computed(() => {
  return true
})
</script>

<template>
  <div
    v-if="isConnected"
    class="w-full max-w-[150px] h-[30px] px-1 py-2 rounded-md bg-disconnected border border-border-primary hover:scale-105 transition-transform duration-300 flex items-center justify-evenly cursor-pointer opacity-90"
  >
    <span class="text-red-500 text-sm">Disconnected</span>
    <Icon name="no_encryption" class="text-red-500" />
  </div>
  <div v-else>
    <div
      class="w-full max-w-[150px] h-[30px] px-2 py-2 rounded-md bg-connected border border-border-primary hover:scale-105 transition-transform duration-300 flex items-center justify-evenly cursor-pointer opacity-90 gap-3"
    >
      <span class="text-green-500 text-sm">Connected</span>
      <Icon name="lock" class="text-green-500" />
    </div>
  </div>
</template>

<style scoped></style>

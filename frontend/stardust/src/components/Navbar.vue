<script setup lang="ts">
import { defineProps } from 'vue'
import Icon from '@/components/Icon.vue'
import Button from '@/components/Buttons/Button.vue'

const props = defineProps<{
  showLogo?: boolean
  isDarkMode?: boolean
  isSticky?: boolean
}>()
</script>

<template>
  <div class="bg-white w-full h-full max-h-[85px] flex items-center justify-between">
    <!-- LOGO + HEADERS -->
    <div class="flex items-center">
      <!-- <img v-if="props.showLogo" /> -->
      <div class="flex flex-col ml-2 items-center justify-between h-full h-max-[52px]">
        <h1 class="text-xl font-bold">Stardust Tunnel</h1>
        <h2 class="text-sm text-gray-200">Free VPN Manager</h2>
      </div>
    </div>
  </div>
</template>

<style scoped></style>

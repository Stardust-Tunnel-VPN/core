<script setup lang="ts">
import { defineProps, computed } from 'vue'
import Icon from '@/components/Icon.vue'
import Button from '@/components/Buttons/Button.vue'

const props = defineProps<{
  showLogo?: boolean
  isDarkMode?: boolean
  isSticky?: boolean
}>()

const iconMode = computed(() => (props.isDarkMode ? 'dark_mode' : 'light_mode'))
</script>

<template>
  <div
    class="bg-white w-full h-full max-h-[85px] flex items-center justify-around border-b-[1px] border-gray-200 px-10 py-10"
  >
    <!-- LOGO + HEADERS -->
    <div class="flex items-center gap-2">
      <img
        src="../assets/logo/svg/stardust_logo_3.svg"
        alt="Stardust Logo"
        class="w-[65px] h-[65px] rounded-sm cursor-pointer hover:scale-120 transition-transform duration-300"
      />
      <div class="flex flex-col ml-2 items-start justify-between h-full h-max-[52px]">
        <h1 class="text-xl font-bold">Stardust Tunnel</h1>
        <h2 class="text-sm text-gray-400">Free VPN Manager</h2>
      </div>
    </div>
    <div class="flex gap-6 items-center justify-center">
      <Button text="Explore Stardust 🚀" />
      <Icon :name="iconMode" focused />
    </div>
  </div>
</template>

<style scoped></style>

<script setup lang="ts">
import { defineProps, computed } from 'vue'
import { useDarkModeStore } from '@/stores/darkModeStore'
import Icon from '@/components/Icon.vue'
import Button from '@/components/Buttons/Button.vue'
import Frame from '@/components/Frame.vue'

const props = defineProps<{
  showLogo?: boolean
  isDarkMode?: boolean
  isSticky?: boolean
}>()

const darkModeStore = useDarkModeStore()

function toggleDarkMode() {
  darkModeStore.toggleDarkMode()
}
</script>

<template>
  <div
    class="bg-bg-primary w-full h-full max-h-[85px] flex items-center justify-between border-b-[1px] border-border-primary px-10 py-10"
  >
    <!-- LOGO + HEADERS -->
    <div class="flex items-center gap-2">
      <img
        src="../assets/logo/svg/stardust_logo_3.svg"
        alt="Stardust Logo"
        class="w-[65px] h-[65px] rounded-sm cursor-pointer hover:scale-120 transition-transform duration-300"
      />
      <div class="flex flex-col ml-2 items-start justify-between h-full h-max-[52px]">
        <h1 class="text-xl font-bold text-text-primary">Stardust Tunnel</h1>
        <h2 class="text-sm text-text-secondary">Free VPN Manager</h2>
      </div>
    </div>
    <div class="flex gap-6 items-center justify-center">
      <a
        href="https://synonymous-panda-cec.notion.site/Stardust-Tunnel-Documentation-1c609e377300805ca916c351fa7ae019"
        target="_blank"
        rel="Documentation link"
      >
        <Button text="📖 Explore Stardust" />
      </a>
      <Icon
        v-if="darkModeStore.isDarkMode"
        name="dark_mode"
        class="text-yellow-200 cursor-pointer hover:scale-120 transition-transform duration-300"
        :onclick="toggleDarkMode"
      />
      <Icon
        v-else
        name="light_mode"
        class="text-yellow-300 cursor-pointer hover:scale-120 transition-transform duration-300"
        :onclick="toggleDarkMode"
      />
    </div>
  </div>
</template>

<style scoped></style>

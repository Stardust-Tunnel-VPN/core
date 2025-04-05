<script setup lang="ts">
import { defineProps, computed } from 'vue'
import Frame from '@/components/Frame.vue'
import Icon from '@/components/Icon.vue'

const props = defineProps<{
  currentOs: string
}>()

const systemInfo = computed(() => {
  return {
    name: props.currentOs === 'mac' ? 'macOS' : 'Windows',
    icon: props.currentOs === 'mac' ? 'apple' : 'window',
  }
})
</script>

<template>
  <Frame
    size="medium"
    header-text="Current OS"
    subheader-text="Your current OS. There is a different connection-behavior based on your OS."
  >
    <div class="flex items-center justify-between px-6">
      <div class="flex items-center gap-2 pb-2">
        <span class="text-lg font-bold text-text-primary"
          >Your current OS is {{ systemInfo.name }}</span
        >
        <Icon :name="systemInfo.icon" size="small" />
      </div>
    </div>
  </Frame>
</template>

<style scoped></style>

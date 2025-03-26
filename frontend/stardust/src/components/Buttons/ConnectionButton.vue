<script setup lang="ts">
import { computed, defineProps } from 'vue'
import Button from '@/components/Buttons/Button.vue'

const props = defineProps<{
  isClientConnected: boolean
  size: 'small' | 'medium' | 'large'
}>()

const buttonColours = computed(() => {
  props.isClientConnected ? 'bg-green-500' : 'bg-red-500'
})
</script>

<template>
  <Button
    :text="props.isClientConnected ? 'Connected' : 'Disconnected'"
    :size="props.size"
    :class="buttonColours"
  />
</template>

<style scoped></style>

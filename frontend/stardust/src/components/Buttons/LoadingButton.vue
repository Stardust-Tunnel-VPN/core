<script setup lang="ts">
import { defineProps, defineEmits, computed } from 'vue'
import Button from '@/components/Buttons/Button.vue'
import Icon from '@/components/Icon.vue'

const props = defineProps<{
  isLoading: boolean
  buttonText?: string
}>()

const emit = defineEmits<{
  (e: 'refresh'): void
}>()

const btnText = computed(() => props.buttonText || 'Refresh')

function onRefresh() {
  if (!props.isLoading) {
    emit('refresh')
  }
}
</script>

<template>
  <!-- Оборачиваем Button, чтобы добавить click-событие и использовать слот -->
  <Button @click="onRefresh">
    <div class="flex items-center gap-2">
      <!-- Иконка "sync" с анимацией вращения при hover -->
      <Icon name="sync" class="refresh-icon" />
      <span class="text-text-primary">{{ btnText }}</span>
    </div>
  </Button>
</template>

<style scoped>
.refresh-icon {
  transition: transform 0.3s;
}
.refresh-icon:hover {
  transform: rotate(360deg);
}
</style>

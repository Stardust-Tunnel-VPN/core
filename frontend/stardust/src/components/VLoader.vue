<template>
  <div v-if="isLoading" class="loader-container" :style="loaderDimensions">
    <!-- Передаём Icon, применяя вычисленный размер шрифта через inline-стиль -->
    <Icon
      name="sync"
      :size="size"
      class="loader-icon text-text-primary font-extralight"
      :style="iconStyle"
    />
  </div>
</template>

<script setup lang="ts">
import { defineProps, computed } from 'vue'
import Icon from '@/components/Icon.vue'

const props = defineProps<{
  isLoading: boolean
  size?: 'small' | 'medium' | 'large'
}>()

// Вычисляем размеры контейнера (например, medium = 300px x 300px)
const loaderDimensions = computed(() => {
  const sizes: Record<string, string> = {
    small: '150px',
    medium: '300px',
    large: '450px',
  }
  const sizeVal = sizes[props.size || 'medium']
  return {
    width: sizeVal,
    height: sizeVal,
  }
})

// Вычисляем размер шрифта для иконки, чтобы она выглядела как нужная картинка
const iconStyle = computed(() => {
  // Здесь можно задать размер шрифта, например, 50% от размера контейнера
  const textSizes: Record<string, string> = {
    small: '75px',
    medium: '150px',
    large: '225px',
  }
  return {
    fontSize: textSizes[props.size || 'medium'],
  }
})
</script>

<style scoped>
.loader-container {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Анимация вращения в обратном направлении */
@keyframes spinReverse {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(-360deg);
  }
}

.loader-icon {
  animation: spinReverse 2s linear infinite;
  display: block;
}
</style>

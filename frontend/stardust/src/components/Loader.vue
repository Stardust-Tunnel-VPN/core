<template>
  <div class="flex items-center justify-center h-full">
    <div class="relative">
      <!-- Outer rotating ring -->
      <div
        class="w-24 h-24 border-4 border-dashed border-purple-500 rounded-full animate-spin-slow"
      ></div>

      <!-- Inner pulsating star -->
      <div class="absolute inset-0 flex items-center justify-center">
        <div class="w-12 h-12 bg-yellow-400 rounded-full animate-pulse-star"></div>
      </div>

      <!-- JoJo reference text -->
      <div class="absolute inset-0 flex items-center justify-center">
        <p class="text-purple-700 font-bold text-lg animate-text-flicker">ザ・ワールド</p>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'Loader',
})
</script>

<style>
@keyframes spin-slow {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@keyframes pulse-star {
  0%,
  100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.5);
    opacity: 0.5;
  }
}

@keyframes text-flicker {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.3;
  }
}

.animate-spin-slow {
  animation: spin-slow 3s linear infinite;
}

.animate-pulse-star {
  animation: pulse-star 1.5s ease-in-out infinite;
}

.animate-text-flicker {
  animation: text-flicker 1.2s ease-in-out infinite;
}
</style>

<!-- TailwindCSS is assumed to be configured in your project -->

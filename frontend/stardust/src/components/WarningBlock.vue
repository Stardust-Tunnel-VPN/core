<script setup lang="ts">
import { computed, ref, defineProps } from 'vue'

const props = defineProps<{
  title: string
}>()
</script>

<template>
  <div
    class="flex flex-col items-center justify-center bg-bg-secondary border-2 border-bg-primary rounded-lg gap-5 px-4"
  >
    <h1 class="font-bold pt-4">{{ props.title }}</h1>
    <div class="text-justify text-text-primary text-md">
      <slot> </slot>
    </div>
  </div>
</template>

<style scoped></style>

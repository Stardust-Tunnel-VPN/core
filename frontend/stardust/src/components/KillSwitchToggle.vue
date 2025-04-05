<template>
  <div
    v-if="!props.isDisabled"
    @click="toggle"
    class="w-12 h-6 bg-gray-300 rounded-full relative cursor-pointer transition-colors duration-300"
    :class="modelValue ? 'bg-main-accent-hover' : 'bg-gray-300'"
  >
    <div
      class="absolute top-0 left-0 w-6 h-6 bg-white rounded-full shadow-md transition-transform duration-300"
      :class="modelValue ? 'translate-x-6' : 'translate-x-0'"
    ></div>
  </div>
  <div
    v-else
    class="w-12 h-6 bg-gray-300 rounded-full relative cursor-not-allowed"
    :class="modelValue ? 'bg-main-accent-hover' : 'bg-gray-300'"
  >
    <div
      class="absolute top-0 left-0 w-6 h-6 bg-white rounded-full shadow-md transition-transform duration-300"
      :class="modelValue ? 'translate-x-6' : 'translate-x-0'"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'

const props = defineProps<{
  modelValue: boolean
  isDisabled?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()

function toggle() {
  if (props.isDisabled) return
  emit('update:modelValue', !props.modelValue)
}
</script>

<style scoped></style>

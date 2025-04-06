<script setup lang="ts">
import { defineProps, defineEmits, ref, defineModel } from 'vue'
import Icon from '@/components/Icon.vue'

const props = defineProps<{
  placeholder?: string
  isPasswordInput?: boolean
}>()

const modelValue = defineModel<string>({
  required: true,
})
</script>

<template>
  <div
    v-if="!props.isPasswordInput"
    class="bg-bg-secondary h-full max-h-[20px] flex items-center justify-end"
  >
    <input
      v-model="modelValue"
      class="relative w-full h-full bg-bg-secondary text-text-primary text-lg px-2 py-2 rounded-md border-border-primary border-2"
      :placeholder="props.placeholder"
    />
  </div>
  <div v-else class="bg-bg-secondary h-full max-h-[20px] flex items-center justify-end">
    <input
      v-model="modelValue"
      type="password"
      class="relative w-full h-full bg-bg-secondary text-text-primary text-lg px-2 py-2 rounded-md border-border-primary border-2"
      :placeholder="props.placeholder"
    />
  </div>
</template>

<style scoped></style>

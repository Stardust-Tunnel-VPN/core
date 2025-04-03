<script setup lang="ts">
import { defineProps, defineEmits, ref, defineModel } from 'vue'
import Icon from '@/components/Icon.vue'

const props = defineProps<{
  placeholder?: string
}>()

const modelValue = defineModel<string>({
  required: true,
})
</script>

<template>
  <div class="bg-bg-secondary h-full max-h-[20px] flex items-center justify-end pt-4">
    <input
      v-model="modelValue"
      class="relative w-full h-full bg-bg-secondary text-text-primary text-lg px-2 py-2 rounded-md border-border-primary border-2"
      :placeholder="props.placeholder"
    />
    <!-- <Icon name="search" class="text-white absolute" /> -->
  </div>
</template>

<style scoped></style>

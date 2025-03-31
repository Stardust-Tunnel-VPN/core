<script setup lang="ts">
import { ref, computed } from 'vue'
import { defineProps, defineEmits } from 'vue'
import type { DropdownOption } from '@/utils/interfaces/dropdown_option'
import Icon from '@/components/Icon.vue'

const props = defineProps<{
  options: DropdownOption<string>[]
  placeholder?: string
  modelValue: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const isOpen = ref(false)

const toggleDropdown = () => {
  isOpen.value = !isOpen.value
}

function selectOption(option: DropdownOption<string>) {
  emit('update:modelValue', option.value)
  isOpen.value = false
}

const selectedOption = computed(() => {
  return props.options.find((opt) => opt.value === props.modelValue)
})

const iconName = computed(() => {
  return isOpen.value ? 'arrow_drop_up' : 'arrow_drop_down'
})
</script>

<template>
  <div class="relative inline-block w-full">
    <div
      @click="toggleDropdown"
      class="cursor-pointer bg-bg-secondary h-full flex items-center justify-between px-2 py-1 rounded-md border-2 border-border-primary"
    >
      <span class="text-text-primary text-xl">
        {{ selectedOption ? selectedOption.label : props.placeholder || 'Select...' }}
      </span>
      <Icon :name="iconName" class="text-text-primary" />
    </div>
    <div
      v-if="isOpen"
      class="absolute z-10 mt-1 w-full bg-bg-secondary rounded-md border border-border-primary"
    >
      <div
        v-for="option in props.options"
        :key="option.value"
        @click="selectOption(option)"
        class="cursor-pointer px-2 py-2 text-text-primary hover:bg-bg-hover text-lg"
      >
        {{ option.label }}
      </div>
    </div>
  </div>
</template>

<style scoped></style>

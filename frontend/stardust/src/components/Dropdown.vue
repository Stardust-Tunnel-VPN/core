<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
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

const dropdownId = Math.random().toString(36).substr(2, 9)
const dropdownRef = ref<HTMLElement | null>(null)

const toggleDropdown = (e?: Event) => {
  if (!isOpen.value) {
    const event = new CustomEvent('dropdown-open', { detail: { id: dropdownId } })
    window.dispatchEvent(event)
  }
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

const handleDocumentClick = (e: MouseEvent) => {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target as Node)) {
    isOpen.value = false
  }
}

const handleOtherDropdownOpen = (e: CustomEvent) => {
  if (e.detail.id !== dropdownId) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleDocumentClick)
  window.addEventListener('dropdown-open', handleOtherDropdownOpen as EventListener)
})

onUnmounted(() => {
  document.removeEventListener('click', handleDocumentClick)
  window.removeEventListener('dropdown-open', handleOtherDropdownOpen as EventListener)
})
</script>

<template>
  <div ref="dropdownRef" class="relative inline-block w-full">
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

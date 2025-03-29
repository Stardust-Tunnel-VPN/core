<script setup lang="ts">
import { ref, computed, defineProps, defineEmits } from 'vue'
import type { DropdownOption } from '@/utils/interfaces/dropdown_option'

const props = defineProps<{
  options: DropdownOption<string>[]
  modelValue: string
}>()

const emit = defineEmits(['update:modelValue'])

const isOpen = ref(false)

/**
 * Toggle dropdown open/close state.
 */
const toggleDropdown = () => {
  isOpen.value = !isOpen.value
}

/**
 * Emit new value and close dropdown.
 * @param value - Selected option value.
 */
const selectOption = (value: string) => {
  emit('update:modelValue', value)
  isOpen.value = false
}

/**
 * Computes label of selected option.
 */
const selectedLabel = computed(() => {
  const found = props.options.find((opt) => opt.value === props.modelValue)
  return found ? found.label : 'Select...'
})
</script>

<template>
  <div class="relative inline-block w-full">
    <!-- Кнопка открытия dropdown -->
    <button
      type="button"
      class="bg-white border border-gray-300 rounded w-full px-4 py-2 text-left"
      @click="toggleDropdown"
    >
      <span>{{ selectedLabel }}</span>
      <!-- Иконка стрелки -->
      <svg
        class="w-4 h-4 inline-block float-right"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M19 9l-7 7-7-7"
        ></path>
      </svg>
    </button>
    <!-- Список опций -->
    <transition name="fade">
      <ul
        v-if="isOpen"
        class="absolute z-10 mt-1 bg-white border border-gray-300 rounded w-full max-h-60 overflow-auto"
      >
        <li
          v-for="option in options"
          :key="option.value"
          class="cursor-pointer hover:bg-gray-100 px-4 py-2"
          @click="selectOption(option.value)"
        >
          {{ option.label }}
        </li>
      </ul>
    </transition>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

<script setup lang="ts">
import { ref, computed, defineProps, defineEmits, defineModel } from 'vue'
import type { DropdownOption } from '@/utils/interfaces/dropdown_option'

const props = defineProps<{
  options: DropdownOption<string>[]
}>()

const emit = defineEmits(['update:modelValue'])

const isOpen = ref(false)

/**
 * Toggle dropdown open/close state.
 */
const toggleDropdown = () => {
  isOpen.value = !isOpen.value
}
</script>

<template></template>

<style scoped></style>

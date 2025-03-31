<script setup lang="ts">
import { defineProps, computed, ref } from 'vue'
import Icon from '@/components/Icon.vue'
import Button from '@/components/Buttons/Button.vue'

const props = defineProps<{
  isLoading: boolean
  buttonText?: string
}>()

const btnText = computed(() => {
  return props.buttonText ? props.buttonText : ' '
})
</script>

<template>
  <div>
    <Icon name="sync" />
    <Button :text="btnText" />
  </div>
</template>

<style scoped></style>

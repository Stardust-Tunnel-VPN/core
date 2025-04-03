<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'
import Icon from '@/components/Icon.vue'

const props = defineProps<{
  visible: boolean
  headerText?: string
  subheaderText?: string
}>()

const emit = defineEmits(['update:visible'])

const onClose = () => {
  emit('update:visible', false)
}
</script>

<template>
  <div v-if="visible" class="fixed inset-0 flex items-center justify-center z-9999">
    <!-- OVERLAY -->
    <div class="absolute inset-0 bg-black opacity-50" @click="onClose"></div>
    <!-- WRAPPER -->
    <div class="relative bg-bg-primary rounded-lg shadow-lg max-w-lg w-full p-6">
      <div class="flex justify-between items-start">
        <div>
          <h1 v-if="headerText" class="text-3xl font-semibold text-text-primary">
            {{ headerText }}
          </h1>
          <h2 v-if="subheaderText" class="text-lg text-text-secondary">
            {{ subheaderText }}
          </h2>
        </div>
        <!-- CLOSE ICON -->
        <Icon name="close" @click="onClose" class="text-text-primary cursor-pointer" />
      </div>
      <!-- MODAL CONTENT -->
      <div class="mt-4">
        <slot />
      </div>
    </div>
  </div>
</template>

<style scoped></style>

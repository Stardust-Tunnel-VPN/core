<script setup lang="ts">
import { ref, defineProps, defineEmits } from 'vue'
import type { IVTableHeaders } from '@/utils/interfaces/vtable_headers'

const props = defineProps<{
  headers: IVTableHeaders[]
  data: any[]
  isLoading?: boolean
}>()
</script>

<template>
  <div
    class="flex items-start justify-between overflow-auto max-h-[325px] px-1 py-1 border-2 border-border-primary rounded-lg"
  >
    <table class="min-w-full border border-border-primary">
      <!-- HEAD SECTION -->
      <thead class="bg-bg-secondary">
        <tr>
          <th
            v-for="header in props.headers"
            :key="header.key"
            class="px-4 py-2 border border-border-primary text-text-primary"
          >
            {{ header.label }}
          </th>
        </tr>
      </thead>
      <!-- BODY SECTION -->
      <tbody>
        <slot name="body" />
      </tbody>
    </table>
  </div>
</template>

<style scoped></style>

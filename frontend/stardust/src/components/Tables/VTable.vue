<script setup lang="ts">
import { ref, defineProps, defineEmits, computed } from 'vue'
import type { IVTableHeaders } from '@/utils/interfaces/vtable_headers'
import VLoader from '@/components/VLoader.vue'

const props = defineProps<{
  headers: IVTableHeaders[]
  data: any[]
  isLoading?: boolean
}>()

const isDataEmpty = computed(() => props.isLoading || props.data.length === 0)
</script>

<template>
  <div
    v-if="!isDataEmpty"
    class="flex items-start justify-between overflow-y-auto overflow-x-hidden scrollbar-dark max-h-[425px] rounded-lg"
  >
    <table class="min-w-full border-[1px] border-border-primary">
      <!-- HEAD SECTION -->
      <thead class="bg-bg-secondary border-[1px] rounded-md border-border-primary">
        <tr class="">
          <th
            v-for="header in props.headers"
            :key="header.key"
            class="py-2 text-text-primary font-bold"
          >
            {{ header.label }}
          </th>
        </tr>
      </thead>
      <!-- BODY SECTION -->
      <tbody>
        <slot v-if="!isDataEmpty" name="body" />
      </tbody>
    </table>
  </div>
  <div v-else class="flex items-center justify-center w-full min-h-[525px]">
    <VLoader :is-loading="isDataEmpty" size="medium" />
  </div>
</template>

<style scoped></style>

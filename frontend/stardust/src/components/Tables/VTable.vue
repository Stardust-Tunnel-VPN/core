<script setup lang="ts">
import { ref, defineProps, defineEmits, computed } from 'vue'
import type { IVTableHeaders } from '@/utils/interfaces/vtable_headers'

const props = defineProps<{
  headers: IVTableHeaders[]
  data: any[]
  isLoading?: boolean
}>()

const isDataEmpty = computed(() => props.data.length === 0)
</script>

<template>
  <div
    class="flex items-start justify-between overflow-y-auto overflow-x-hidden scrollbar-dark max-h-[525px] rounded-lg"
  >
    <table class="min-w-full min-h-[525px] border-[1px] border-border-primary">
      <!-- HEAD SECTION -->
      <thead class="bg-bg-secondary border-[1px] rounded-md border-border-primary">
        <tr class="">
          <th
            v-for="header in props.headers"
            :key="header.key"
            class="py-2 text-text-primary font-mono font-extralight"
          >
            {{ header.label }}
          </th>
        </tr>
      </thead>
      <!-- BODY SECTION -->
      <tbody>
        <slot v-if="!isDataEmpty" name="body" />
        <tr v-else>
          <!-- TODO: implement & provide 'empty-list' component or loader -->
          <td :colspan="props.headers.length" class="py-4 text-center text-text-primary font-mono">
            {{ props.isLoading ? 'Loading...' : 'No data avaliable; Try to refresh' }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped></style>

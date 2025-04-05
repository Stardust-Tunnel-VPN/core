<script setup lang="ts">
import ServersList from '@/components/ServersList.vue'

const props = defineProps<{
  currentOs: string
}>()
</script>

<template>
  <body class="bg-bg-secondary h-screen p-4">
    <ServersList :current-os="props.currentOs" />
  </body>
</template>

<style scoped></style>

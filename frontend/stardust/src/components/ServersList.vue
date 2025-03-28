<script setup lang="ts">
import Frame from '@/components/Frame.vue'
import Button from '@/components/Button.vue'
</script>

<template>
  <div class="flex items-center justify-evenly pt-[40px]">
    <div class="flex justify-center">
      <Frame
        size="table"
        headerText="VPN Servers"
        subheaderText="Choose your server"
        bg-color="white"
      >
        <!-- V-MODEL BASED SEARCH, 2 DROPDOWNS (V-MODEL AS WELL) + TABLE -->
      </Frame>
    </div>
    <!-- TODO: make the max gap respectfully to the parent -->
    <div class="flex flex-col gap-10">
      <Frame
        size="medium"
        headerText="Connection status"
        subheaderText="Monitor your VPN connection"
        bg-color="white"
      >
        <!-- CONNECTION-STATUS BUTTON -->
      </Frame>
      <Frame
        size="large"
        headerText="Connection Logs"
        subheaderText="View recent connection activity"
        bg-color="white"
      >
        <!-- CONNECTION-LOGS COMPONENT -->
      </Frame>
    </div>
  </div>
</template>

<style scoped></style>

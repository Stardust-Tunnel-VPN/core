<script setup lang="ts">
import Frame from '@/components/Frame.vue'
import ConnectionLogs from '@/components/ConnectionLogs.vue'
import ConnectionButton from '@/components/Buttons/ConnectionButton.vue'
import Icon from '@/components/Icon.vue'
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
        <!-- CONNECTION-STATUS BUTTON TODO: get rid of 'text' prop later - do it based on the store.-->
        <div class="flex flex-row items-center justify-between px-6">
          <ConnectionButton text="Disconnected" />
          <Icon name="signal_disconnected" class="text-main-accent" variant="outlined" />
        </div>
      </Frame>
      <Frame
        size="large"
        headerText="Connection Logs"
        subheaderText="View recent connection activity"
        bg-color="white"
      >
        <!-- CONNECTION-LOGS COMPONENT -->
        <div class="w-full h-full flex items-start justify-center">
          <ConnectionLogs />
        </div>
      </Frame>
    </div>
  </div>
</template>

<style scoped></style>

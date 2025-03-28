<script setup lang="ts">
import { defineProps } from 'vue'
import Loader from '@/components/Loader.vue'
import Frame from '@/components/Frame.vue'
import Icon from '@/components/Icon.vue'
import Input from '@/components/Input.vue'
import Navbar from '@/components/Navbar.vue'
import Home from '@/views/Home.vue'
</script>

<template>
  <header>
    <div class="wrapper">
      <Navbar showLogo />
    </div>
  </header>
  <Home />
</template>

<style scoped></style>

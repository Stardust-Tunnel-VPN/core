<script setup lang="ts">
import { computed, ref } from 'vue'
import { useConnectionLogsStore } from '@/stores/connectionLogsStore'

const logsStore = useConnectionLogsStore()

const logs = computed(() =>
  logsStore.logs.length ? logsStore.logs.map((log) => `> ${log}`) : ['No logs available'],
)

const userInput = ref('')

function handleEnter() {
  const command = userInput.value.trim()
  if (command) {
    logsStore.addLog(command)
    logsStore.addLog('Oops! Nuclear warheads have been launched at the communists! 🚀☢️')
    userInput.value = ''
  }
}
</script>

<template>
  <div
    class="terminal-container hover-refresh w-full max-w-[315px] h-full max-h-[190px] bg-[#0f2d0f] p-3 rounded-md overflow-y-auto scrollbar-hide hover:scale-103 transition-transform duration-300"
  >
    <span class="terminal-title block text-green-300 text-xl font-mono mb-2"
      >Connection Logs...</span
    >
    <div class="flex flex-col space-y-1">
      <div
        v-for="(log, index) in logs"
        :key="index"
        class="terminal-log text-green-400 text-sm font-mono"
      >
        {{ log }}
      </div>
    </div>
    <div class="flex items-center mt-12">
      <span
        class="blinking-caret text-green-400 font-mono font-extrabold text-xl mr-2"
        style="transform: scaleX(2)"
        >|</span
      >
      <input
        type="text"
        v-model="userInput"
        @keydown.enter="handleEnter"
        placeholder="Type command..."
        class="flex-1 bg-transparent border-none outline-none text-green-400 font-mono text-base placeholder-green-500"
      />
    </div>
  </div>
</template>

<style scoped>
/* 
Some of this kind of unique animations I decided to put in this <style> section instead of over-engineer it with tailwind. I'd assume that it's impossibe to achieve this animations results with pure tailwindCSS so this is the correct place IMHO.
*/
.terminal-container {
  background-color: #0f2d0f;
  box-shadow: 0 0 7px 2px rgba(0, 255, 0, 0.6);
  position: relative;
  background-image: repeating-linear-gradient(
    to bottom,
    transparent 0,
    transparent 2px,
    rgba(0, 0, 0, 0.05) 2px,
    rgba(0, 0, 0, 0.05) 4px
  );
  background-size: 100% 4px;
}

@keyframes refreshScan {
  from {
    background-position: 0 0;
  }
  to {
    background-position: 0 4px;
  }
}

.hover-refresh:hover {
  animation: refreshScan 4s linear infinite;
}

.terminal-log {
  padding-bottom: 0.25rem;
}

@keyframes blink {
  0%,
  50% {
    opacity: 1;
  }
  51%,
  100% {
    opacity: 0;
  }
}
.blinking-caret {
  animation: blink 1s step-start infinite;
}
</style>

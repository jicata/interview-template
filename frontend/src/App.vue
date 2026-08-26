<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { get } from './api/client'
import ReorderPanel from './components/ReorderPanel.vue'

interface HelloResponse {
  message: string
}

const message = ref<string | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    const data = await get<HelloResponse>('/hello')
    message.value = data.message
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Unknown error'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div style="font-family: sans-serif; max-width: 800px; margin: 2rem auto; padding: 0 1rem">
    <h1>Interview Template</h1>
    <p v-if="loading">Loading...</p>
    <p v-else-if="error" style="color: red">Error: {{ error }}</p>
    <p v-else>{{ message }}</p>

    <ReorderPanel />
  </div>
</template>

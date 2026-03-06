<template>
  <div>
    <h2 class="text-2xl mb-4">Juegos mejor valorados</h2>
    <div v-if="loading" class="text-gray-500">Cargando...</div>
    <div v-else-if="error" class="text-red-500">{{ error }}</div>
    <ul v-else class="space-y-2">
      <li v-for="game in games" :key="game.id" class="p-2 bg-white rounded shadow">
        <h3 class="font-semibold">{{ game.title }}</h3>
        <p class="text-sm text-gray-600">Calificación: {{ game.average_rating }}</p>
      </li>
      <li v-if="!games.length" class="text-gray-600">No hay juegos disponibles.</li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const games = ref([])
const loading = ref(false)
const error = ref(null)

async function fetchTopRated() {
  loading.value = true
  error.value = null
  try {
    const res = await fetch('/api/games/top-rated')
    if (!res.ok) throw new Error('Error al obtener datos')
    games.value = await res.json()
  } catch (err) {
    console.error(err)
    error.value = 'No se pudieron cargar los juegos.'
  } finally {
    loading.value = false
  }
}

onMounted(fetchTopRated)
</script>

<style scoped></style>
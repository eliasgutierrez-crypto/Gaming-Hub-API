<template>
  <div>
    <h2 class="text-2xl mb-4">Top Rated Games</h2>
    <ul class="space-y-2">
      <li v-for="game in games" :key="game.id" class="p-2 bg-white rounded shadow">
        <h3 class="font-semibold">{{ game.title }}</h3>
        <p class="text-sm text-gray-600">Rating: {{ game.average_rating }}</p>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const games = ref([])

async function fetchTopRated() {
  try {
    const res = await fetch('/api/games/top-rated')
    games.value = await res.json()
  } catch (err) {
    console.error(err)
  }
}

onMounted(fetchTopRated)
</script>

<style scoped></style>
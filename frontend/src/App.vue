<template>
  <div class="min-h-screen bg-gray-100">
    <header class="bg-blue-600 text-white p-4">
      <h1 class="text-xl font-bold">Gaming Hub</h1> <!-- nombre de la aplicación, puede dejarse en inglés -->
    </header>
    <main class="p-4">
      <GameList />
    </main>
  </div>
</template>

<script setup>
import GameList from './components/GameList.vue'
</script>

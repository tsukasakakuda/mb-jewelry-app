<template>
    <div class="max-w-3xl mx-auto p-6 bg-white rounded shadow">
      <h1 class="text-2xl font-bold mb-4">アイテム詳細</h1>
      <div v-if="item">
        <p><strong>event ID:</strong> {{ item.event_id }}</p>
        <p><strong>Box ID:</strong> {{ item.box_id }}</p>
        <p><strong>Box No:</strong> {{ item.box_no }}</p>
        <p><strong>Material:</strong> {{ item.material }}</p>
        <p><strong>Misc:</strong> {{ item.misc }}</p>
        <p><strong>Weight:</strong> {{ item.weight }}</p>
        <p><strong>Jewelry Price:</strong> {{ item.jewelry_price }}</p>
        <p><strong>Material Price:</strong> {{ item.material_price }}</p>
        <!-- 必要な項目を追加 -->
      </div>
      <div v-else class="text-gray-600">読み込み中または存在しません。</div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import { useRoute } from 'vue-router'
  import axios from 'axios'
  
  const route = useRoute()
  const item = ref(null)
  const baseURL = import.meta.env.VITE_API_BASE
  
  onMounted(async () => {
    try {
      const response = await axios.get(`${baseURL}/items/${route.params.id}`)
      item.value = response.data
    } catch (err) {
      console.error(err)
    }
  })
  </script>
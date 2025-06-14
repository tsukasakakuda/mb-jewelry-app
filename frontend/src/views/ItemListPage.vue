<template>
    <div class="p-6 max-w-6xl mx-auto">
      <h1 class="text-2xl font-bold mb-4">登録済み地金アイテム一覧</h1>
  
      <table class="min-w-full border border-gray-300">
        <thead class="bg-gray-100">
          <tr>
            <th class="p-2 border">ID</th>
            <th class="p-2 border">Box ID</th>
            <th class="p-2 border">Box No</th>
            <th class="p-2 border">Material</th>
            <th class="p-2 border">Weight</th>
            <th class="p-2 border">Price</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id" @click="$router.push(`/items/${item.id}`)" class="cursor-pointer hover:bg-gray-100">
            <td class="p-2 border">{{ item.event_id }}</td>
            <td class="p-2 border">{{ item.box_id }}</td>
            <td class="p-2 border">{{ item.box_no }}</td>
            <td class="p-2 border">{{ item.material }}</td>
            <td class="p-2 border">{{ item.weight }}</td>
            <td class="p-2 border">{{ item.jewelry_price }}</td>
          </tr>
        </tbody>
      </table>
  
      <div v-if="errorMessage" class="text-red-600 mt-4">{{ errorMessage }}</div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import axios from 'axios'
  
  const items = ref([])
  const errorMessage = ref('')
  const baseURL = import.meta.env.VITE_API_BASE
  
  onMounted(async () => {
    try {
      const response = await axios.get(`${baseURL}/items`)
      items.value = response.data
    } catch (error) {
      errorMessage.value = 'データの取得に失敗しました。'
    }
  })
  </script>
<template>
    <div class="min-h-screen bg-white p-6 w-full">
      <div class="max-w-4xl mx-auto space-y-6">
        <h1 class="text-2xl font-bold text-gray-800 text-center">
          CSVアップロードで地金アイテム登録
        </h1>
  
        <form @submit.prevent="submitCSV" class="space-y-4">
          <div>
            <label class="block font-semibold text-gray-700 mb-1">item_csv</label>
            <input
              type="file"
              @change="onItemChange"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-md bg-white"
            />
          </div>
          <div>
            <label class="block font-semibold text-gray-700 mb-1">price_csv</label>
            <input
              type="file"
              @change="onPriceChange"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-md bg-white"
            />
          </div>
          <button
            type="submit"
            class="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
          >
            アップロード
          </button>
        </form>
  
        <div v-if="successMessage" class="text-green-600 font-semibold mt-4">
          {{ successMessage }}
        </div>
        <div v-if="errorMessage" class="text-red-600 font-semibold mt-4">
          {{ errorMessage }}
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import axios from 'axios'
  
  const baseURL = import.meta.env.VITE_API_BASE
  
  const itemCSVFile = ref(null)
  const priceCSVFile = ref(null)
  const successMessage = ref('')
  const errorMessage = ref('')
  
  const onItemChange = (e) => {
    itemCSVFile.value = e.target.files[0]
  }
  
  const onPriceChange = (e) => {
    priceCSVFile.value = e.target.files[0]
  }
  
  const submitCSV = async () => {
    successMessage.value = ''
    errorMessage.value = ''
  
    const formData = new FormData()
    formData.append('item_csv', itemCSVFile.value)
    formData.append('price_csv', priceCSVFile.value)
  
    try {
      const response = await axios.post(`${baseURL}/upload-items`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
  
      const data = response.data
  
      if (data.invalid_weights && data.invalid_weights.length > 0) {
        errorMessage.value = '重量に誤りがあるデータが含まれています。修正してください。'
        successMessage.value = ''
        return
      }
  
      if (data.message) {
        successMessage.value = data.message
        errorMessage.value = ''
      }
  
    } catch (error) {
      errorMessage.value = '登録に失敗しました：' + (error.response?.data?.error || error.message)
      successMessage.value = ''
    }
  }
  </script>
  
  <style scoped>
  </style>
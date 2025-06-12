<template>
    <div class="max-w-xl mx-auto py-10 px-4">
      <h1 class="text-2xl font-bold mb-6 text-center">CSVで地金アイテム登録</h1>
  
      <form @submit.prevent="submitCsv" class="space-y-4">
        <div>
          <label class="block font-semibold mb-1">item_csv</label>
          <input type="file" @change="onItemCsvChange" required />
        </div>
        <div>
          <label class="block font-semibold mb-1">price_csv</label>
          <input type="file" @change="onPriceCsvChange" required />
        </div>
        <button type="submit" class="bg-blue-600 text-white px-4 py-2 rounded">アップロード</button>
      </form>
  
      <p v-if="message" class="mt-4 text-green-600 font-medium">{{ message }}</p>
      <p v-if="error" class="mt-4 text-red-600 font-medium">{{ error }}</p>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import axios from 'axios'
  
  const itemCsv = ref(null)
  const priceCsv = ref(null)
  const message = ref('')
  const error = ref('')
  
  const onItemCsvChange = (e) => {
    itemCsv.value = e.target.files[0]
  }
  const onPriceCsvChange = (e) => {
    priceCsv.value = e.target.files[0]
  }
  
  const submitCsv = async () => {
    message.value = ''
    error.value = ''
    const formData = new FormData()
    formData.append('item_csv', itemCsv.value)
    formData.append('price_csv', priceCsv.value)
  
    try {
      const res = await axios.post('http://127.0.0.1:8080/upload-items', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      message.value = '登録が完了しました'
    } catch (err) {
      error.value = '登録に失敗しました: ' + (err.response?.data?.error || err.message)
    }
  }
  </script>
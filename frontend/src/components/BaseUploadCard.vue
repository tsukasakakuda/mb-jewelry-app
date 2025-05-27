<template>
    <!--<div class="flex flex-col items-center justify-center min-h-screen bg-white">-->
    <div class="max-w-4xl mx-auto space-y-6">
      <h1 class="text-2xl font-bold text-gray-800">{{ title }}</h1>
  
      <div class="flex flex-col gap-4 w-full max-w-md px-4">
        <div v-for="(field, index) in fileFields" :key="index">
          <span class="block font-semibold text-gray-700 mb-1">{{ field.label }}</span>
          <input
            type="file"
            @change="event => handleFileChange(event, field.name)"
            class="w-full px-4 py-2 border border-gray-300 rounded-md bg-white"
          />
        </div>
  
        <button
          @click="onSubmit"
          class="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-md"
        >
          {{ buttonText }}
        </button>
      </div>
    </div>
  </template>
  
  <script>

  export default {
    props: {
      title: String,
      fileFields: Array, // 例: [{ name: 'item_csv', label: 'item_csv' }]
      onSubmit: Function,
      buttonText: {
        type: String,
      default: 'アップロード' // 任意のデフォルト
      }
    },
    data() {
      return {
        selectedFiles: {},
      };
    },
    methods: {
      handleFileChange(event, fieldName) {
        this.selectedFiles[fieldName] = event.target.files[0];
        this.$emit("update:files", this.selectedFiles); // 親にファイルを送信
      },
    },
  };
  </script>
  <style scoped>
  input[type="file"]::-webkit-file-upload-button {
    background: #e2e8f0;
    border: 1px solid #cbd5e0;
    border-radius: 4px;
    padding: 0.3rem 0.75rem;
    font-size: 0.875rem;
    cursor: pointer;
  }
  </style>
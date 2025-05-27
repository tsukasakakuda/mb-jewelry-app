<template>
    <div class="space-y-4">
      <h2 class="text-xl font-bold">CSV 編集ツール</h2>
      <input type="file" @change="onFileChange" class="border p-2" />
      <button @click="submitFile" class="bg-blue-600 text-white px-4 py-2 rounded">編集してダウンロード</button>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        file: null,
        baseURL: import.meta.env.VITE_API_BASE
      };
    },
    methods: {
      onFileChange(e) {
        this.file = e.target.files[0];
      },
      async submitFile() {
        if (!this.file) {
          alert("CSVファイルを選択してください");
          return;
        }
  
        const formData = new FormData();
        formData.append("file", this.file);
  
        try {
          const res = await fetch(`${this.baseURL}/edit-csv`, {
            method: "POST",
            body: formData
          });
  
          const blob = await res.blob();
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement("a");
          link.href = url;
          link.setAttribute("download", "edited_csv.csv");
          document.body.appendChild(link);
          link.click();
          link.remove();
          window.URL.revokeObjectURL(url);
        } catch (err) {
          console.error("エラー:", err);
          alert("編集処理に失敗しました");
        }
      }
    }
  };
  </script>
<template>
  <div class="min-h-screen bg-white p-6 w-full">
    <div class="max-w-2xl mx-auto space-y-6">
      <h1 class="text-2xl font-bold text-gray-800 text-center">
        CSV 編集ツール
      </h1>

      <form @submit.prevent="submitCsv" class="space-y-4">
        <div>
          <label class="block font-semibold text-gray-700 mb-1">CSVファイル</label>
          <input
            type="file"
            @change="onFileChange"
            required
            class="w-full px-4 py-2 border border-gray-300 rounded-md bg-white"
          />
        </div>
        <div class="text-center">
          <button
            type="submit"
            class="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-md"
          >
            編集してダウンロード
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      selectedFile: null,
      baseURL: import.meta.env.VITE_API_BASE
    };
  },
  methods: {
    onFileChange(e) {
      this.selectedFile = e.target.files[0] || null;
    },
    async submitCsv() {
      if (!this.selectedFile) {
        alert("ファイルを選択してください");
        return;
      }

      const formData = new FormData();
      formData.append("file", this.selectedFile);

      try {
        const res = await fetch(`${this.baseURL}/edit-csv`, {
          method: "POST",
          body: formData
        });

        if (!res.ok) {
          throw new Error("エラーが発生しました");
        }

        const disposition = res.headers.get("Content-Disposition");
        const match = disposition && disposition.match(/filename="?(.+)"?/);
        const filename = match ? match[1] : "edited_result.csv";

        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", filename);
        document.body.appendChild(link);
        link.click();
        window.URL.revokeObjectURL(url);
      } catch (err) {
        console.error("submitCsvエラー:", err);
        alert("CSV編集に失敗しました");
      }
    }
  }
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
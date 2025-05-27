<template>
  <BaseUploadCard
    title="CSV 編集ツール"
    :fileFields="[{ name: 'file', label: 'CSVファイル' }]"
    :onSubmit="handleSubmit"
    @update:files="files => selectedFile = files.file"
  />
</template>

<script>
import BaseUploadCard from "@/components/BaseUploadCard.vue";

export default {
  components: { BaseUploadCard },
  data() {
    return {
      selectedFile: null,
    };
  },
  methods: {
    async handleSubmit() {
      if (!this.selectedFile) {
        alert("ファイルを選択してください");
        return;
      }

      const formData = new FormData();
      formData.append("file", this.selectedFile);

      const res = await fetch(`${import.meta.env.VITE_API_BASE}/edit-csv`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        alert("エラーが発生しました");
        return;
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "edited_csv.csv";
      link.click();
      window.URL.revokeObjectURL(url);
    },
  },
};
</script>
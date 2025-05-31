<template>
  <div class="min-h-screen bg-white p-6 w-full">
    <div class="max-w-4xl mx-auto space-y-6">
      <h1 class="text-2xl font-bold text-gray-800 text-center">
        地金自動計算
      </h1>

      <form @submit.prevent="checkWeights" class="space-y-4">
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
        <div class="text-center">
          <button
            type="submit"
            class="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-md"
          >
            アップロードしてチェック
          </button>
        </div>
      </form>

      <div v-if="invalidWeights.length">
        <h2 class="text-lg font-semibold text-red-600">修正が必要なデータ</h2>
        <table class="table-auto w-full text-sm border">
          <thead>
            <tr>
              <th class="border px-2">box_id</th>
              <th class="border px-2">box_no</th>
              <th class="border px-2">material</th>
              <th class="border px-2">misc</th>
              <th class="border px-2">weight（修正可）</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, idx) in invalidWeights" :key="idx">
              <td class="border px-2">{{ item.box_id }}</td>
              <td class="border px-2">{{ item.box_no }}</td>
              <td class="border px-2">{{ item.row_data.material }}</td>
              <td class="border px-2">{{ item.row_data.misc }}</td>
              <td class="border px-2">
                <input v-model="item.row_data.weight" class="border px-1 rounded w-full" />
              </td>
            </tr>
          </tbody>
        </table>
        <div class="text-right mt-4">
          <button
            @click="submitFixedData"
            class="bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700"
          >
            修正して再計算（CSVダウンロード）
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      itemFile: null,
      priceFile: null,
      priceData: [],
      invalidWeights: [],
      allItems: [],
      validItems: [],
      baseURL: import.meta.env.VITE_API_BASE,
    };
  },
  methods: {
    onItemChange(e) {
      this.itemFile = e.target.files[0] || null;
    },
    async onPriceChange(e) {
      this.priceFile = e.target.files[0] || null;
      if (!this.priceFile) return;

      const text = await this.priceFile.text();
      const rows = text.trim().split('\n');
      const headers = rows[0].split(',');
      this.priceData = rows.slice(1).map(row => {
        const values = row.split(',');
        const obj = {};
        headers.forEach((h, i) => obj[h.trim()] = values[i]?.trim() ?? '');
        return obj;
      });
    },
    async checkWeights() {
      if (!this.itemFile || !this.priceFile) {
        alert("両方のCSVファイルを選択してください");
        return;
      }

      const formData = new FormData();
      formData.append("item_file", this.itemFile);

      const text = await this.itemFile.text();
      const rows = text.trim().split('\n');
      const headers = rows[0].split(',');
      this.allItems = rows.slice(1).map((row, index) => {
        const values = row.split(',');
        const obj = {};
        headers.forEach((h, i) => obj[h.trim()] = values[i]?.trim() ?? '');
        obj.original_index = index;
        return obj;
      });

      try {
        const res = await fetch(`${this.baseURL}/check-weights`, {
          method: "POST",
          body: formData
        });
        const data = await res.json();
        this.invalidWeights = data.invalid_weights || [];

        const errorIndexes = new Set(this.invalidWeights.map(w => w.index));
        this.validItems = this.allItems.filter((_, idx) => !errorIndexes.has(idx));

        if (this.invalidWeights.length === 0) {
          this.submitFixedData();
        }
      } catch (err) {
        console.error("checkWeightsエラー:", err);
        alert("CSVチェックに失敗しました");
      }
    },
    async submitFixedData() {
      const fixedItems = this.invalidWeights.map(w => w.row_data);
      const mergedItems = [...this.validItems, ...fixedItems];

      const payload = {
        item_data: mergedItems,
        price_data: this.priceData
      };

      try {
        const res = await fetch(`${this.baseURL}/calculate-fixed`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        const disposition = res.headers.get("Content-Disposition");
        const match = disposition && disposition.match(/filename="?(.+)"?/);
        const filename = match ? match[1] : "calculated_result.csv";

        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", filename);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
      } catch (err) {
        console.error("submitFixedDataエラー:", err);
        alert("再計算に失敗しました");
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
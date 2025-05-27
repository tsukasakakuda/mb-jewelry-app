<template>
  <div class="min-h-screen bg-white p-6 w-full">
    <CsvEditor />
  </div>
</template>

<script>
import CsvEditor from '../components/CsvEditor.vue'

export default {
  name: 'CsvEditorPage',
  components: {
    CsvEditor
  }
}
</script>
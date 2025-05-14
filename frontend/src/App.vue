<template>
  <div class="min-h-screen bg-gray-100 p-8">
    <UploadForm />
  </div>
</template>

<script>
import UploadForm from './components/UploadForm.vue';

export default {
  components: {
    UploadForm
  }
};
</script>

<style>
body {
  font-family: 'Helvetica', sans-serif;
}
</style>
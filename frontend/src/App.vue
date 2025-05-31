<template>
  <div class="flex flex-col md:flex-row min-h-screen">
    <SidebarMenu class="md:w-64 w-full md:block bg-gray-100" />
    <main class="flex-1 bg-white p-6">
      <router-view />
    </main>
  </div>
</template>

<script>
import SidebarMenu from './components/SidebarMenu.vue';
export default { components: { SidebarMenu } };
</script>

<style>
body {
  font-family: 'Helvetica', sans-serif;
  margin: 0;
}
</style>
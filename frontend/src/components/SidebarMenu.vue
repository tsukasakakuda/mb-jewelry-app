<template>
    <div class="relative">
      <!-- ハンバーガーアイコン -->
      <button @click="toggleMenu" class="md:hidden p-2 focus:outline-none">
        <svg class="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M4 6h16M4 12h16M4 18h16"/>
        </svg>
      </button>
  
      <!-- モバイル用メニュー -->
      <div :class="['absolute bg-white border shadow-lg mt-2 w-48 z-50', isOpen ? 'block' : 'hidden']">
        <ul>
          <li class="p-4 hover:bg-gray-100">
            <router-link to="/" @click="closeMenu">メニュー</router-link>
          </li>
          <li class="p-4 hover:bg-gray-100">
            <router-link to="/calculate" @click="closeMenu">地金計算</router-link>
          </li>
          <li class="p-4 hover:bg-gray-100">
            <router-link to="/csv" @click="closeMenu">CSV加工</router-link>
          </li>
          <li class="p-4 hover:bg-gray-100">
            <router-link to="/login" @click="closeMenu">ログイン</router-link>
          </li>
        </ul>
      </div>
  
      <!-- PC用サイドメニュー -->
      <div class="hidden md:block bg-white border-r w-48 h-screen p-4">
        <ul class="space-y-4">
          <li>
            <router-link to="/" class="text-gray-700 hover:underline">メニュー</router-link>
          </li>
          <li>
            <router-link to="/calculate" class="text-gray-700 hover:underline">地金計算</router-link>
          </li>
          <li>
            <router-link to="/csv" class="text-gray-700 hover:underline">CSV加工</router-link>
          </li>
          <li>
            <router-link to="/login" class="text-gray-700 hover:underline">ログイン</router-link>
          </li>
        </ul>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        isOpen: false
      };
    },
    methods: {
      toggleMenu() {
        this.isOpen = !this.isOpen;
      },
      closeMenu() {
        this.isOpen = false;
      }
    }
  };
  </script>
  
  <style scoped>
  /* スタイルは必要に応じて追加 */
  </style>
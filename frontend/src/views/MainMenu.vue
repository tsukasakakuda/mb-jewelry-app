<template>
    <div class="text-center space-y-6">
      <h1 class="text-3xl font-bold text-gray-800">メインメニュー</h1>
      <div class="space-y-4">
        <router-link to="/calculate" class="block bg-blue-600 text-white py-3 rounded hover:bg-blue-700">
          地金自動計算
        </router-link>
        <router-link to="/csv" class="block bg-green-600 text-white py-3 rounded hover:bg-green-700">
          CSV加工ツール
        </router-link>
      </div>
    </div>
  </template>
import { createRouter, createWebHistory } from 'vue-router';
import MainMenu from '@/views/MainMenu.vue';
//import UploadForm from '@/views/UploadForm.vue';
import LoginPage from '@/views/LoginPage.vue';
import CsvEditorPage from '@/views/CsvEditorPage.vue';
import UploadItemPage from '@/views/UploadItemPage.vue';
import ItemListPage from '@/views/ItemListPage.vue';
import ItemDetailPage from '@/views/ItemDetailPage.vue';
import MetalCalculatePage from '@/views/MetalCalculatePage.vue';

const routes = [
  { path: '/', name: 'MainMenu', component: MainMenu },
  { path: '/calculate', name: 'MetalCalculatePage', component: MetalCalculatePage },
  { path: '/upload-items', name: 'UploadItemPage', component: UploadItemPage },
  { path: '/item-list', name: 'ItemList', component: ItemListPage },
  { path: '/items/:id', name: 'ItemDetail', component: ItemDetailPage},
  //{ path: '/calculate', name: 'UploadForm', component: UploadForm },
  { path: '/login', name: 'LoginPage', component: LoginPage },
  { path: '/csv', name: 'CsvEditor', component: CsvEditorPage }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
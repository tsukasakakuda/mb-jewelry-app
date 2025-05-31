import { createRouter, createWebHistory } from 'vue-router';
import MainMenu from '@/views/MainMenu.vue';
//import UploadForm from '@/views/UploadForm.vue';
import LoginPage from '@/views/LoginPage.vue';
import CsvEditorPage from '@/views/CsvEditorPage.vue';
import MetalCalculatePage from '@/views/MetalCalculatePage.vue';

const routes = [
  { path: '/', name: 'MainMenu', component: MainMenu },
  { path: '/calculate', name: 'MetalCalculatePage', component: MetalCalculatePage },
  //{ path: '/calculate', name: 'UploadForm', component: UploadForm },
  { path: '/login', name: 'LoginPage', component: LoginPage },
  { path: '/csv', name: 'CsvEditor', component: CsvEditorPage }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
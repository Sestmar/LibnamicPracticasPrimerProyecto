import './assets/main.css' // (Opcional, puede que no esté y no pasa nada)

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router' // <--- IMPORTANTE: Importar el router

const app = createApp(App)

app.use(createPinia())
app.use(router) // <--- IMPORTANTE: Usar el router

app.mount('#app')
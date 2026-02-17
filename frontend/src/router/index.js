import { createRouter, createWebHistory } from 'vue-router'
// Importo las vistas directamente para evitar problemas de carga
import LoginView from '../views/LoginView.vue'
import ProductsView from '../views/ProductsView.vue'
import MyOrdersView from '../views/MyOrdersView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      // Ruta raíz: Redirige automáticamente al login
      path: '/',
      redirect: '/login'
    },
    {
      // Ruta del Login
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      // Ruta de los Productos
      path: '/products',
      name: 'products',
      component: ProductsView
    },
    {
      path: '/my-orders',
      name: 'my-orders',
      component: MyOrdersView
    }
  ]
})

export default router
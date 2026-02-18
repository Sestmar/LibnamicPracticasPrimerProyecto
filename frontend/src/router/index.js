import { createRouter, createWebHistory } from 'vue-router'
// Importo las vistas directamente para evitar problemas de carga
import LoginView from '../views/LoginView.vue'
import ProductsView from '../views/ProductsView.vue'
import MyOrdersView from '../views/MyOrdersView.vue'
import CartView from '../views/CartView.vue'
import AdminDashboardView from '../views/AdminDashboardView.vue'
import RegisterView from '../views/RegisterView.vue'
import PaymentView from '../views/PaymentView.vue'
import ChatView from '../views/ChatView.vue'

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
    },
    {
      path: '/cart',
      name: 'cart',
      component: CartView
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminDashboardView
    },
    {
      path: '/register',
      name: 'register', component: RegisterView
    },
    {
      path: '/payment',
      name: 'payment',
      component: PaymentView
    },
    {
      path: '/chat',
      name: 'chat',
      component: ChatView
    }
  ]
})

export default router
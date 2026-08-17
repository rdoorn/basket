import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import CalendarView from './views/CalendarView.vue'

const routes: RouteRecordRaw[] = [
  { path: '/', name: 'calendar', component: CalendarView },
  { path: '/buy', name: 'buy', component: () => import('./views/BuyView.vue') },
  {
    path: '/recipe/new',
    name: 'recipe-new',
    component: () => import('./views/RecipeEditView.vue'),
  },
  {
    path: '/recipe/:id',
    name: 'recipe-detail',
    component: () => import('./views/RecipeDetailView.vue'),
    props: true,
  },
  {
    path: '/recipe/:id/edit',
    name: 'recipe-edit',
    component: () => import('./views/RecipeEditView.vue'),
    props: true,
  },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router

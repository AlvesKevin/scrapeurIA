import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'dashboard',
    component: () => import('@/views/Dashboard.vue')
  },
  {
    path: '/tasks/new',
    name: 'new-task',
    component: () => import('@/views/NewTask.vue')
  },
  {
    path: '/results/:taskId',
    name: 'results',
    component: () => import('@/views/Results.vue')
  },
  {
    path: '/templates',
    name: 'templates',
    component: () => import('@/views/Templates.vue')
  }
]

export const router = createRouter({
  history: createWebHistory(),
  routes
}) 
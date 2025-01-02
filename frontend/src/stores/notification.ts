import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Notification } from '@/types'

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref<Notification[]>([])

  const addNotification = (notification: Omit<Notification, 'id'>) => {
    const id = Math.random().toString(36).substring(2)
    const newNotification = {
      ...notification,
      id,
      duration: notification.duration ?? 5000
    }
    
    notifications.value.push(newNotification)
    
    // Auto-suppression après la durée spécifiée
    setTimeout(() => {
      removeNotification(id)
    }, newNotification.duration)
  }

  const removeNotification = (id: string) => {
    notifications.value = notifications.value.filter(n => n.id !== id)
  }

  return {
    notifications,
    addNotification,
    removeNotification
  }
}) 
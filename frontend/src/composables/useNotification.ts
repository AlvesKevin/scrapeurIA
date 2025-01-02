import { ref } from 'vue'

interface Notification {
  message: string
  type: 'success' | 'error' | 'warning' | 'info'
  id: number
}

const notifications = ref<Notification[]>([])
let nextId = 0

export function useNotification() {
  const showNotification = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info') => {
    const id = nextId++
    const notification = {
      id,
      message,
      type
    }
    
    notifications.value.push(notification)
    
    setTimeout(() => {
      removeNotification(id)
    }, 5000)
  }

  const removeNotification = (id: number) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  return {
    notifications,
    showNotification,
    removeNotification
  }
} 
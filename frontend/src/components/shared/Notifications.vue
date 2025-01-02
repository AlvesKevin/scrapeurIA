<template>
  <div class="fixed bottom-0 right-0 p-6 z-50">
    <TransitionGroup
      name="notification"
      tag="div"
      class="space-y-2"
    >
      <div
        v-for="notification in notifications"
        :key="notification.id"
        :class="[
          'max-w-sm w-full bg-white shadow-lg rounded-lg pointer-events-auto ring-1 ring-black ring-opacity-5',
          getNotificationClass(notification.type)
        ]"
      >
        <div class="p-4">
          <div class="flex items-start">
            <div class="flex-shrink-0">
              <Icon
                :name="getNotificationIcon(notification.type)"
                class="h-6 w-6"
                :class="getIconClass(notification.type)"
              />
            </div>
            <div class="ml-3 w-0 flex-1">
              <p class="text-sm font-medium text-gray-900">
                {{ notification.message }}
              </p>
            </div>
            <div class="ml-4 flex-shrink-0 flex">
              <button
                class="rounded-md inline-flex text-gray-400 hover:text-gray-500 focus:outline-none"
                @click="removeNotification(notification.id)"
              >
                <span class="sr-only">Fermer</span>
                <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { useNotification } from '@/composables/useNotification'
import Icon from './Icon.vue'

const { notifications, removeNotification } = useNotification()

const getNotificationClass = (type: string) => {
  switch (type) {
    case 'success':
      return 'bg-green-50 ring-green-500'
    case 'error':
      return 'bg-red-50 ring-red-500'
    case 'warning':
      return 'bg-yellow-50 ring-yellow-500'
    default:
      return 'bg-blue-50 ring-blue-500'
  }
}

const getNotificationIcon = (type: string) => {
  switch (type) {
    case 'success':
      return 'check-circle'
    case 'error':
      return 'x-circle'
    case 'warning':
      return 'exclamation'
    default:
      return 'information'
  }
}

const getIconClass = (type: string) => {
  switch (type) {
    case 'success':
      return 'text-green-500'
    case 'error':
      return 'text-red-500'
    case 'warning':
      return 'text-yellow-500'
    default:
      return 'text-blue-500'
  }
}
</script>

<style scoped>
.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style> 
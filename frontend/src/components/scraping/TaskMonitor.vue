<template>
  <div class="bg-white shadow rounded-lg p-6">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold">Tâches de Scraping</h2>
      <button
        @click="refreshTasks"
        class="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
      >
        Rafraîchir
      </button>
    </div>
    
    <div v-if="store.loading" class="text-center py-4">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
    </div>
    
    <div v-else-if="store.error" class="text-red-600 p-4 text-center">
      {{ store.error }}
    </div>
    
    <div v-else-if="store.tasks.length === 0" class="text-gray-500 text-center py-4">
      Aucune tâche trouvée
    </div>
    
    <div v-else class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Date
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              URL
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Description
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Statut
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="task in store.tasks" :key="task._id || task.id">
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ formatDate(task.created_at) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm text-gray-900 truncate max-w-xs">
                {{ task.url }}
              </div>
            </td>
            <td class="px-6 py-4">
              <div class="text-sm text-gray-900">{{ task.description }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="getStatusClass(task.status)" class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full">
                {{ task.status }}
              </span>
              <div v-if="task.metadata?.error" class="text-xs text-red-600 mt-1">
                {{ task.metadata.error }}
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <div class="flex space-x-2">
                <button
                  v-if="task.status === 'pending'"
                  @click="executeTask(getTaskId(task))"
                  class="text-indigo-600 hover:text-indigo-900"
                >
                  Exécuter
                </button>
                <button
                  v-if="task.status === 'running'"
                  disabled
                  class="text-gray-400"
                >
                  En cours...
                </button>
                <router-link
                  v-if="task.status === 'completed'"
                  :to="`/results/${task._id}`"
                  class="text-green-600 hover:text-green-900"
                >
                  Voir résultats
                </router-link>
                <button
                  v-if="task.status === 'failed'"
                  @click="retryTask(task._id)"
                  class="text-yellow-600 hover:text-yellow-900"
                >
                  Réessayer
                </button>
                <button
                  @click="() => {
                    console.log('Delete button clicked for task:', {
                      task,
                      id: task._id || task.id
                    })
                    deleteTask(getTaskId(task))
                  }"
                  class="text-red-600 hover:text-red-900 ml-2"
                >
                  Supprimer
                </button>
                <button
                  @click="showLogs(task)"
                  class="text-blue-600 hover:text-blue-900"
                >
                  Logs
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal pour les logs -->
    <Modal v-if="showLogsModal" @close="showLogsModal = false">
      <template #header>
        <h3 class="text-lg font-medium">Logs de la tâche</h3>
      </template>
      <template #body>
        <div class="bg-gray-100 p-4 rounded-lg max-h-96 overflow-y-auto">
          <div v-for="(log, index) in selectedTaskLogs" :key="index" class="mb-2">
            <div class="text-xs text-gray-500">{{ formatDate(log.timestamp) }}</div>
            <div :class="getLogLevelClass(log.level)">{{ log.message }}</div>
          </div>
        </div>
      </template>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useScrapingStore } from '@/stores/scraping'
import Modal from '@/components/shared/Modal.vue'
import { useNotification } from '@/composables/useNotification'
import type { Task } from '@/types'

const store = useScrapingStore()
const { showNotification } = useNotification()

const showLogsModal = ref(false)
const selectedTaskLogs = ref<any[]>([])

// Rafraîchissement automatique toutes les 10 secondes pour les tâches en cours
let refreshInterval: number | null = null

onMounted(async () => {
  await refreshTasks()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
})

const startAutoRefresh = () => {
  refreshInterval = window.setInterval(async () => {
    if (store.tasks.some(task => task.status === 'running')) {
      await refreshTasks()
    }
  }, 10000)
}

const stopAutoRefresh = () => {
  if (refreshInterval) {
    window.clearInterval(refreshInterval)
  }
}

const refreshTasks = async () => {
  await store.fetchTasks()
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleString()
}

const getStatusClass = (status: string) => {
  const classes = {
    pending: 'bg-yellow-100 text-yellow-800',
    running: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800'
  }
  return classes[status as keyof typeof classes] || 'bg-gray-100 text-gray-800'
}

const executeTask = async (taskId: string) => {
  try {
    if (!taskId) {
      showNotification("ID de tâche invalide", 'error')
      return
    }
    console.log('Executing task with ID:', taskId)
    await store.executeTask(taskId)
    showNotification('Tâche lancée avec succès', 'success')
    await refreshTasks()
  } catch (error) {
    console.error('Error executing task:', error)
    showNotification("Erreur lors du lancement de la tâche", 'error')
  }
}

const retryTask = async (taskId: string) => {
  try {
    await store.retryTask(taskId)
    showNotification('Tâche relancée avec succès', 'success')
    await refreshTasks()
  } catch (error) {
    showNotification("Erreur lors de la relance de la tâche", 'error')
  }
}

const deleteTask = async (taskId: string) => {
  try {
    console.log('Attempting to delete task with ID:', taskId)
    
    if (!taskId) {
      showNotification("ID de tâche invalide", 'error')
      return
    }
    
    if (confirm('Êtes-vous sûr de vouloir supprimer cette tâche ?')) {
      await store.deleteTask(taskId)
      showNotification('Tâche supprimée avec succès', 'success')
      await refreshTasks()
    }
  } catch (error) {
    console.error('Error deleting task:', error)
    showNotification("Erreur lors de la suppression de la tâche", 'error')
  }
}

const showLogs = async (task: any) => {
  try {
    selectedTaskLogs.value = await store.getTaskLogs(task.id)
    showLogsModal.value = true
  } catch (error) {
    showNotification("Erreur lors de la récupération des logs", 'error')
  }
}

const getLogLevelClass = (level: string) => {
  const classes = {
    info: 'text-blue-600',
    error: 'text-red-600',
    warning: 'text-yellow-600'
  }
  return classes[level as keyof typeof classes] || 'text-gray-600'
}

// Fonction utilitaire pour obtenir l'ID de la tâche
const getTaskId = (task: Task): string => {
  if (!task) {
    throw new Error('Task is undefined')
  }

  // Log pour debug
  console.log('Task structure:', {
    task,
    _id: task._id,
    rawTask: JSON.stringify(task)
  })

  // Vérifie si l'ID est dans _id (structure MongoDB)
  if (task._id) {
    if (typeof task._id === 'string') {
      return task._id
    }
    if (typeof task._id === 'object' && '$oid' in task._id) {
      return task._id.$oid
    }
  }

  // Vérifie si l'ID est dans id (nouvelle structure)
  if (task.id) {
    if (typeof task.id === 'string') {
      return task.id
    }
    if (typeof task.id === 'object' && '$oid' in task.id) {
      return task.id.$oid
    }
  }

  throw new Error('Invalid task ID format')
}
</script> 
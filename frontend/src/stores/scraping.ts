import { defineStore } from 'pinia'
import { api } from '@/services/api'
import type { Task, TaskCreate, MongoDBId } from '@/types'

interface State {
  tasks: Task[]
  currentTask: Task | null
  loading: boolean
  error: string | null
}

const getTaskId = (task: Task): string => {
  // Vérifie _id (format MongoDB)
  if (task._id) {
    if (typeof task._id === 'string') return task._id
    if (typeof task._id === 'object' && '$oid' in task._id) return task._id.$oid
  }
  
  // Vérifie id (nouveau format)
  if (task.id) {
    if (typeof task.id === 'string') return task.id
    if (typeof task.id === 'object' && '$oid' in task.id) return task.id.$oid
  }
  
  throw new Error('Invalid task ID format')
}

export const useScrapingStore = defineStore('scraping', {
  state: (): State => ({
    tasks: [],
    currentTask: null,
    loading: false,
    error: null
  }),

  actions: {
    async fetchTasks() {
      this.loading = true
      try {
        const response = await api.get('/tasks')
        console.log('Tasks reçues du backend:', response.data)
        
        this.tasks = response.data.map((task: any) => {
          // Assure-toi que l'ID est présent dans _id pour la compatibilité
          const taskWithId = {
            ...task,
            _id: task._id || task.id || { $oid: task.$oid }
          }
          console.log('Task transformée:', taskWithId)
          return taskWithId
        })
        
        console.log('Tasks après transformation:', this.tasks)
      } catch (error) {
        this.error = 'Erreur lors du chargement des tâches'
        console.error('Error fetching tasks:', error)
      } finally {
        this.loading = false
      }
    },

    async createTask(task: TaskCreate) {
      this.loading = true
      try {
        const response = await api.post('/tasks', task)
        await this.fetchTasks()
        return response.data.task_id
      } catch (error) {
        this.error = 'Erreur lors de la création de la tâche'
        console.error('Error creating task:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async executeTask(taskId: string) {
      try {
        console.log('Store: executing task', taskId)
        const response = await api.post(`/tasks/${taskId}/execute`)
        await this.fetchTasks()
        return response.data
      } catch (error) {
        console.error('Store: error executing task:', error)
        this.error = "Erreur lors de l'exécution de la tâche"
        throw error
      }
    },

    async retryTask(taskId: string) {
      try {
        await api.post(`/tasks/${taskId}/retry`)
        await this.fetchTasks()
      } catch (error) {
        this.error = "Erreur lors de la relance de la tâche"
        throw error
      }
    },

    async deleteTask(taskId: string) {
      try {
        console.log('Deleting task with ID:', taskId)
        await api.delete(`/tasks/${taskId}`)
        this.tasks = this.tasks.filter(task => getTaskId(task) !== taskId)
        return true
      } catch (error) {
        console.error('Error in deleteTask:', error)
        this.error = "Erreur lors de la suppression de la tâche"
        throw error
      }
    },

    async getTaskLogs(taskId: string) {
      try {
        const response = await api.get(`/tasks/${taskId}/logs`)
        return response.data
      } catch (error) {
        this.error = "Erreur lors de la récupération des logs"
        throw error
      }
    },

    async getTaskResults(taskId: string) {
      try {
        const response = await api.get(`/tasks/${taskId}/results`)
        console.log('Résultats reçus:', response.data)
        return response.data
      } catch (error) {
        console.error('Error fetching results:', error)
        throw error
      }
    },
  }
}) 
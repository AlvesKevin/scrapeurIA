import { config } from '@/config'
import { useScrapingStore } from '@/stores/scraping'
import { useNotification } from '@/composables/useNotification'

export class WebSocketService {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private readonly maxReconnectAttempts = 5

  constructor() {
    this.connect()
  }

  private connect() {
    this.ws = new WebSocket(`${config.wsBaseUrl}/ws/scraping`)
    
    this.ws.onopen = () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
    }

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      this.handleMessage(data)
    }

    this.ws.onclose = () => {
      console.log('WebSocket disconnected')
      this.handleReconnect()
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
  }

  private handleMessage(data: any) {
    const scrapingStore = useScrapingStore()
    const { showNotification } = useNotification()

    switch (data.type) {
      case 'task_update':
        scrapingStore.updateTask(data.task)
        break
      case 'task_complete':
        scrapingStore.updateTask(data.task)
        showNotification('Tâche terminée avec succès', 'success')
        break
      case 'task_error':
        scrapingStore.updateTask(data.task)
        showNotification(data.error, 'error')
        break
    }
  }

  private handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 10000)
      setTimeout(() => this.connect(), delay)
    }
  }

  public send(message: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    }
  }
}

export const wsService = new WebSocketService() 
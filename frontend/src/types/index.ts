// Statuts possibles d'une tâche
export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed'

// Configuration d'une tâche de scraping
export interface ScrapingConfig {
  pagination: boolean
  maxPages?: number
  selectors: Record<string, string>
  navigationRules?: Record<string, any>
  extractionMethod: string
  restrictions: string[]
}

// Tâche de scraping
export interface MongoDBOid {
  $oid: string
}

export type MongoDBId = string | MongoDBOid

export interface Task {
  id: MongoDBId
  url: string
  description: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  created_at: string
  updated_at?: string
  config: any
  results_id?: string
  template_id?: string
  metadata: Record<string, any>
}

// Métadonnées des résultats
export interface ResultMetadata {
  total_items: number
  processing_time: number
  processed_urls: string[]
  extraction_date: string
  quality_score?: number
  [key: string]: any
}

// Résultats d'une tâche de scraping
export interface TaskResult {
  id: string
  task_id: string
  data: any[]
  status: string
  created_at: string
  updated_at?: string
  metadata: Record<string, any>
}

// Configuration d'un template
export interface Template {
  id: string
  name: string
  description: string
  site_pattern: string
  config: ScrapingConfig
  created_at: string
  updated_at?: string
  usage_count: number
  metadata: Record<string, any>
}

// Type pour les notifications
export interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  message: string
  duration?: number
}

export interface TaskCreate {
  url: string
  description: string
  config?: Record<string, any>
  export_format?: string
} 
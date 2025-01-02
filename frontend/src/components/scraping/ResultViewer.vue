<template>
  <div class="bg-white shadow rounded-lg p-6">
    <div v-if="loading" class="text-center">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
    </div>
    
    <div v-else-if="error" class="text-red-600 text-center">
      {{ error }}
    </div>
    
    <div v-else-if="!results?.data?.length" class="text-center text-gray-500">
      Aucun résultat trouvé
    </div>
    
    <div v-else>
      <h2 class="text-xl font-bold mb-4">Résultats du scraping</h2>
      
      <!-- Métadonnées -->
      <div class="mb-4 text-sm text-gray-600">
        <p>Total éléments: {{ results.metadata.total_items }}</p>
        <p>Date d'extraction: {{ formatDate(results.metadata.extraction_date) }}</p>
        <p>Temps de traitement: {{ results.metadata.processing_time.toFixed(2) }}s</p>
      </div>

      <!-- Tableau des résultats -->
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <!-- En-têtes dynamiques basés sur les clés du premier résultat -->
              <th
                v-for="key in Object.keys(results.data[0])"
                :key="key"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                {{ formatHeader(key) }}
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="(item, index) in results.data" :key="index">
              <td
                v-for="key in Object.keys(item)"
                :key="key"
                class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
              >
                <!-- Affiche les tableaux et les objets de manière lisible -->
                <template v-if="Array.isArray(item[key])">
                  {{ item[key].join(', ') }}
                </template>
                <template v-else-if="typeof item[key] === 'object' && item[key] !== null">
                  {{ JSON.stringify(item[key]) }}
                </template>
                <template v-else>
                  {{ item[key] }}
                </template>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useScrapingStore } from '@/stores/scraping'

const route = useRoute()
const store = useScrapingStore()
const results = ref<any>(null)
const loading = ref(true)
const error = ref<string | null>(null)

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString()
}

const formatHeader = (key: string) => {
  return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

onMounted(async () => {
  try {
    loading.value = true
    const taskId = route.params.taskId as string
    if (!taskId) {
      throw new Error('ID de tâche manquant')
    }
    console.log('Chargement des résultats pour la tâche:', taskId)
    const response = await store.getTaskResults(taskId)
    console.log('Résultats reçus:', response)
    results.value = response
  } catch (e) {
    console.error('Erreur lors du chargement des résultats:', e)
    error.value = "Erreur lors du chargement des résultats"
  } finally {
    loading.value = false
  }
})
</script> 
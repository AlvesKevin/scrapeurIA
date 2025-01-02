<template>
  <div class="bg-white p-6 rounded-lg shadow">
    <h2 class="text-2xl font-bold mb-6">Nouvelle tâche de scraping</h2>
    
    <form @submit.prevent="submitForm" class="space-y-6">
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">URL du site</label>
          <input
            v-model="formData.url"
            type="url"
            required
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            placeholder="https://example.com"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700">Description des données à extraire</label>
          <textarea
            v-model="formData.description"
            required
            rows="4"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            placeholder="Décrivez les données que vous souhaitez extraire..."
          ></textarea>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700">Configuration de pagination</label>
          <div class="mt-2 space-y-2">
            <label class="inline-flex items-center">
              <input
                v-model="formData.config.pagination"
                type="checkbox"
                class="rounded border-gray-300 text-indigo-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              />
              <span class="ml-2">Activer la pagination</span>
            </label>
            
            <div v-if="formData.config.pagination">
              <input
                v-model.number="formData.config.maxPages"
                type="number"
                min="1"
                class="mt-1 block w-32 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                placeholder="Max pages"
              />
            </div>
          </div>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700">Format d'export</label>
          <select
            v-model="formData.exportFormat"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          >
            <option value="json">JSON</option>
            <option value="csv">CSV</option>
            <option value="excel">Excel</option>
          </select>
        </div>
      </div>
      
      <div class="flex justify-end space-x-4">
        <button
          type="button"
          @click="resetForm"
          class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Réinitialiser
        </button>
        <button
          type="submit"
          :disabled="loading"
          class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
        >
          {{ loading ? 'Création...' : 'Créer la tâche' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useScrapingStore } from '@/stores/scraping'
import { useNotification } from '@/composables/useNotification'

const scrapingStore = useScrapingStore()
const { showNotification } = useNotification()

const loading = ref(false)

const formData = reactive({
  url: '',
  description: '',
  config: {
    pagination: false,
    maxPages: 10
  },
  exportFormat: 'json'
})

const submitForm = async () => {
  try {
    loading.value = true
    const taskId = await scrapingStore.createTask(formData)
    showNotification('Tâche créée avec succès', 'success')
    resetForm()
  } catch (error) {
    showNotification(
      error instanceof Error ? error.message : 'Erreur lors de la création de la tâche',
      'error'
    )
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  formData.url = ''
  formData.description = ''
  formData.config.pagination = false
  formData.config.maxPages = 10
  formData.exportFormat = 'json'
}
</script> 
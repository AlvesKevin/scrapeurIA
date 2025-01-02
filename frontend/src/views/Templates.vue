<template>
  <div class="container mx-auto px-4 py-8">
    <div class="bg-white p-6 rounded-lg shadow">
      <h2 class="text-2xl font-bold mb-6">Templates de Scraping</h2>
      
      <div class="mb-6">
        <button
          @click="showCreateModal = true"
          class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
        >
          Créer un template
        </button>
      </div>
      
      <!-- Liste des templates -->
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Nom
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Description
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Pattern URL
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Utilisations
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="template in templates" :key="template.id">
              <td class="px-6 py-4 whitespace-nowrap">{{ template.name }}</td>
              <td class="px-6 py-4">{{ template.description }}</td>
              <td class="px-6 py-4">{{ template.site_pattern }}</td>
              <td class="px-6 py-4">{{ template.usage_count }}</td>
              <td class="px-6 py-4">
                <button
                  @click="editTemplate(template)"
                  class="text-indigo-600 hover:text-indigo-900 mr-3"
                >
                  Modifier
                </button>
                <button
                  @click="deleteTemplate(template.id)"
                  class="text-red-600 hover:text-red-900"
                >
                  Supprimer
                </button>
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
import { useScrapingStore } from '@/stores/scraping'
import { useNotification } from '@/composables/useNotification'
import type { Template } from '@/types'

const scrapingStore = useScrapingStore()
const { showNotification } = useNotification()

const templates = ref<Template[]>([])
const showCreateModal = ref(false)

onMounted(async () => {
  try {
    // À implémenter : Chargement des templates
    // templates.value = await scrapingStore.getTemplates()
  } catch (error) {
    showNotification('Erreur lors du chargement des templates', 'error')
  }
})

const editTemplate = (template: Template) => {
  // À implémenter
}

const deleteTemplate = async (id: string) => {
  // À implémenter
}
</script> 
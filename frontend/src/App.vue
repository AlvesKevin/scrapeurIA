<template>
  <div class="min-h-screen bg-gray-100">
    <nav class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex">
            <router-link
              to="/"
              class="flex-shrink-0 flex items-center"
            >
              Scraping Platform
            </router-link>
            <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
              <router-link
                to="/"
                class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
              >
                Dashboard
              </router-link>
              <router-link
                to="/tasks/new"
                class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
              >
                Nouvelle Tâche
              </router-link>
              <router-link
                to="/templates"
                class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
              >
                Templates
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <main>
      <router-view></router-view>
    </main>

    <Notifications />
  </div>
</template>

<script setup lang="ts">
import Notifications from '@/components/shared/Notifications.vue'
</script> 
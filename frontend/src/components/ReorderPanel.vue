<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { get, post } from '../api/client'
import { useBasket } from '../composables/useBasket'
import type { Customer, DraftOrder, ReorderSuggestion } from '../types/reorder'

const customers = ref<Customer[]>([])
const selectedCustomerId = ref<number | null>(null)

const suggestions = ref<ReorderSuggestion[]>([])
const suggestionsLoading = ref(false)
const suggestionsError = ref<string | null>(null)

const basket = useBasket()

const saving = ref(false)
const saveError = ref<string | null>(null)
const savedDraft = ref<DraftOrder | null>(null)

onMounted(async () => {
  try {
    customers.value = await get<Customer[]>('/customers')
    if (customers.value.length > 0) {
      selectedCustomerId.value = customers.value[0].id
    }
  } catch (e) {
    suggestionsError.value = e instanceof Error ? e.message : 'Unknown error'
  }
})

async function loadSuggestions(customerId: number) {
  suggestionsLoading.value = true
  suggestionsError.value = null
  try {
    suggestions.value = await get<ReorderSuggestion[]>(
      `/customers/${customerId}/reorder-suggestions`,
    )
  } catch (e) {
    suggestionsError.value = e instanceof Error ? e.message : 'Unknown error'
    suggestions.value = []
  } finally {
    suggestionsLoading.value = false
  }
}

// Switching customers with a pending selection is unspecified in the PRD
// (flagged for triage in the QA charter) — clearing the basket is the safe
// default, since carrying a basket built against one customer's suggestions
// over to another customer's draft would silently mix the two.
watch(selectedCustomerId, (customerId) => {
  basket.clear()
  savedDraft.value = null
  saveError.value = null
  if (customerId !== null) {
    loadSuggestions(customerId)
  }
})

function toggleSuggestion(suggestion: ReorderSuggestion, checked: boolean) {
  if (checked) {
    basket.add(suggestion)
  } else {
    basket.remove(suggestion.product_id)
  }
}

async function save() {
  if (selectedCustomerId.value === null || basket.lines().length === 0) return

  saving.value = true
  saveError.value = null
  try {
    const draft = await post<DraftOrder>(
      `/customers/${selectedCustomerId.value}/draft/lines`,
      { lines: basket.lines() },
    )
    savedDraft.value = draft
    basket.clear()
  } catch (e) {
    // Selection survives a failed save so the user can retry.
    saveError.value = e instanceof Error ? e.message : 'Unknown error'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <section style="margin-top: 2rem; border-top: 1px solid #ddd; padding-top: 1rem">
    <h2>Reorder suggestions</h2>

    <label>
      Customer:
      <select v-model.number="selectedCustomerId">
        <option v-for="customer in customers" :key="customer.id" :value="customer.id">
          {{ customer.name }}
        </option>
      </select>
    </label>

    <p v-if="suggestionsLoading">Loading suggestions...</p>
    <p v-else-if="suggestionsError" style="color: red">Error: {{ suggestionsError }}</p>
    <p v-else-if="suggestions.length === 0">Nothing due for reorder right now.</p>
    <table v-else>
      <thead>
        <tr>
          <th></th>
          <th>Product</th>
          <th>Suggested qty</th>
          <th>Days overdue</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="suggestion in suggestions" :key="suggestion.product_id">
          <td>
            <input
              type="checkbox"
              :checked="basket.has(suggestion.product_id)"
              @change="toggleSuggestion(suggestion, ($event.target as HTMLInputElement).checked)"
            />
          </td>
          <td>{{ suggestion.name }} ({{ suggestion.sku }})</td>
          <td>{{ suggestion.suggested_quantity }}</td>
          <td>{{ suggestion.days_overdue }}</td>
        </tr>
      </tbody>
    </table>

    <div v-if="basket.items.value.length > 0" style="margin-top: 1rem">
      <h3>Selected</h3>
      <ul>
        <li v-for="item in basket.items.value" :key="item.product_id">
          {{ item.name }} ({{ item.sku }}) — qty {{ item.quantity }}
        </li>
      </ul>
      <button :disabled="saving" @click="save">
        {{ saving ? 'Saving...' : 'Save' }}
      </button>
      <p v-if="saveError" style="color: red">Save failed: {{ saveError }}</p>
    </div>

    <div v-if="savedDraft" style="margin-top: 1rem">
      <h3>Draft order #{{ savedDraft.id }}</h3>
      <ul>
        <li v-for="line in savedDraft.lines" :key="line.product_id">
          {{ line.name }} ({{ line.sku }}) — qty {{ line.quantity }} @ {{ line.unit_price }}
        </li>
      </ul>
    </div>
  </section>
</template>

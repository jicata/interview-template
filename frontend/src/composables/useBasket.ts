import { computed, ref } from 'vue'
import type { DraftLineInput, ReorderSuggestion } from '../types/reorder'

interface BasketLine {
  product_id: number
  name: string
  sku: string
  unit_price: number
  quantity: number
}

// The one piece of real logic on the frontend. Ticking a suggestion is the
// only quantity control the user has — the PRD puts editing the suggested
// quantity out of scope — so add() must merge by product rather than ever
// appending a second line for the same product.
export function useBasket() {
  const entries = ref<Map<number, BasketLine>>(new Map())

  function add(suggestion: ReorderSuggestion): void {
    const existing = entries.value.get(suggestion.product_id)
    if (existing) {
      existing.quantity += suggestion.pack_size
    } else {
      entries.value.set(suggestion.product_id, {
        product_id: suggestion.product_id,
        name: suggestion.name,
        sku: suggestion.sku,
        unit_price: suggestion.unit_price,
        quantity: suggestion.suggested_quantity,
      })
    }
  }

  function remove(productId: number): void {
    entries.value.delete(productId)
  }

  function clear(): void {
    entries.value.clear()
  }

  function has(productId: number): boolean {
    return entries.value.has(productId)
  }

  function lines(): DraftLineInput[] {
    return Array.from(entries.value.values()).map((entry) => ({
      product_id: entry.product_id,
      quantity: entry.quantity,
    }))
  }

  const items = computed<BasketLine[]>(() => Array.from(entries.value.values()))

  return { add, remove, clear, has, lines, items }
}

import { computed, ref } from 'vue'
import type { DraftLineInput, ReorderSuggestion } from '../types/reorder'

interface BasketLine {
  product_id: number
  name: string
  sku: string
  unit_price: number
  quantity: number
}

// Stages suggestions for one batched save. The checkbox UI (ReorderPanel)
// only ever calls add() for a product not already staged — the checkbox's
// `checked` state IS `has(product_id)`, so a second tick always routes to
// remove() instead. There is therefore no reachable path that re-adds an
// already-staged product in this session, and no merge-by-quantity branch
// here: the PRD puts "editing the suggested quantity before saving" out of
// scope, and the AC's "individually selected and deselected" is checkbox
// (binary) semantics. Ticking the same product again after a save — i.e.
// selecting a still-overdue suggestion a second time — is a fresh add() in
// a fresh basket, and increases the draft quantity via #3's backend
// increment rule, not via any client-side merge.
export function useBasket() {
  const entries = ref<Map<number, BasketLine>>(new Map())

  function add(suggestion: ReorderSuggestion): void {
    entries.value.set(suggestion.product_id, {
      product_id: suggestion.product_id,
      name: suggestion.name,
      sku: suggestion.sku,
      unit_price: suggestion.unit_price,
      quantity: suggestion.suggested_quantity,
    })
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

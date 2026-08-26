<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { del, get, post } from './api/client'

/**
 * The seeded draft the task points at — `backend/data/orders.csv` row 19:
 * customer 1, status `draft`, no lines.
 *
 * Reading it on mount, rather than creating a fresh order each time, is what
 * makes a page reload show the lines you just added. A screen that can only
 * display state it holds in memory is indistinguishable from one that never
 * saved anything.
 */
const DRAFT_ORDER_ID = 19

interface Product {
  id: number
  name: string
  sku: string
  unit_price: number
  pack_size: number
}

interface OrderLine {
  id: number
  product_id: number
  product_name: string
  quantity: number
  unit_price: number
  discount_rate: number
  discount_amount: number
  line_total: number
}

interface Order {
  id: number
  customer_id: number
  status: string
  order_date: string | null
  lines: OrderLine[]
  order_total: number
}

const products = ref<Product[]>([])
const order = ref<Order | null>(null)

const loading = ref(true)
const loadError = ref<string | null>(null)
const submitting = ref(false)
const removingLineId = ref<number | null>(null)
const rejection = ref<string | null>(null)

const productId = ref<number | null>(null)

/**
 * What `v-model` on a `type="number"` input genuinely puts here — and the
 * declared type has to say so, because nothing else will.
 *
 * Vue turns on number casting for `type="number"` on its own; the `.number`
 * modifier is implied, not required (`runtime-dom`, `vModelText.created`:
 * `castToNumber = number || props.type === 'number'`). The cast runs through
 * `looseToNumber`, which returns its input *unchanged* when `parseFloat` fails.
 * So a parseable field assigns a `number` and an emptied one assigns the raw
 * `''`, and this ref really does hold both.
 *
 * Typing it as `string` is what broke the Add-line button: `.trim()` on the
 * number threw inside the computed below, the render effect died with it, and
 * `:disabled` kept the last value it had managed to render. Typing it as
 * `number | null` would have failed the same way one layer over — `vue-tsc`
 * cannot see through `v-model`, so a wrong annotation here is invisible to
 * every gate in the repo.
 */
const quantityInput = ref<number | ''>('')

const quantity = computed(() =>
  quantityInput.value === '' ? null : quantityInput.value,
)

const selectedProduct = computed(
  () => products.value.find((p) => p.id === productId.value) ?? null,
)

const packSize = computed(() => selectedProduct.value?.pack_size ?? 1)

const packHint = computed(() => {
  const product = selectedProduct.value
  if (!product) return 'Pick a product to see its pack size.'
  return `Ships in packs of ${product.pack_size} at ${money(product.unit_price)} per unit.`
})

const canSubmit = computed(
  () =>
    !submitting.value &&
    productId.value !== null &&
    quantity.value !== null &&
    Number.isInteger(quantity.value) &&
    quantity.value > 0,
)

onMounted(async () => {
  try {
    const [catalogue, draft] = await Promise.all([
      get<Product[]>('/products'),
      get<Order>(`/orders/${DRAFT_ORDER_ID}`),
    ])
    products.value = catalogue
    order.value = draft
  } catch (e) {
    loadError.value = messageOf(e)
  } finally {
    loading.value = false
  }
})

async function addLine() {
  if (!canSubmit.value) return
  submitting.value = true
  rejection.value = null
  try {
    // The response is the whole recomputed order, so the running total needs no
    // second request.
    order.value = await post<Order>(`/orders/${DRAFT_ORDER_ID}/lines`, {
      product_id: productId.value,
      quantity: quantity.value,
    })
    quantityInput.value = ''
  } catch (e) {
    // The pack-size rule belongs to the server, so the server's sentence is
    // what gets shown. Re-checking it here would be a second source of truth
    // that could disagree with the one that actually rejects the write.
    rejection.value = messageOf(e)
  } finally {
    submitting.value = false
  }
}

async function removeLine(lineId: number) {
  removingLineId.value = lineId
  rejection.value = null
  try {
    order.value = await del<Order>(`/orders/${DRAFT_ORDER_ID}/lines/${lineId}`)
  } catch (e) {
    rejection.value = messageOf(e)
  } finally {
    removingLineId.value = null
  }
}

function money(value: number): string {
  return value.toFixed(2)
}

function discountLabel(line: OrderLine): string {
  if (line.discount_rate === 0) return '—'
  return `${Math.round(line.discount_rate * 100)}% (−${money(line.discount_amount)})`
}

function messageOf(e: unknown): string {
  return e instanceof Error ? e.message : 'Something went wrong.'
}
</script>

<template>
  <main class="page">
    <h1>Order Builder</h1>

    <p v-if="loading" class="muted">Loading…</p>
    <p v-else-if="loadError" class="banner banner--error">{{ loadError }}</p>

    <template v-else-if="order">
      <p class="muted">
        Order #{{ order.id }} · customer {{ order.customer_id }} ·
        <span class="pill">{{ order.status }}</span>
      </p>

      <!--
        novalidate: the server owns the pack-size rule, and its sentence is what
        the user is meant to read. Native validation would abort the submit
        before `@submit` ever fired — no event, no request, no message, nothing
        on screen. The min/step pair below is an affordance, not a second gate.
      -->
      <form class="add-line" novalidate @submit.prevent="addLine">
        <div class="field field--grow">
          <label for="product">Product</label>
          <select id="product" v-model="productId">
            <option :value="null" disabled>Select a product…</option>
            <option v-for="product in products" :key="product.id" :value="product.id">
              {{ product.name }} ({{ product.sku }})
            </option>
          </select>
        </div>

        <div class="field">
          <label for="quantity">Quantity</label>
          <!--
            `step` counts from `min`, not from zero. Binding both to the pack
            size makes the valid values 12, 24, 36 for a pack of 12 — the pack
            multiples exactly, and the spinner arrows move one pack at a time.
            The previous `min="1"` made the step base 1, so the arrows walked
            1, 13, 25 and every real pack multiple was flagged invalid.
          -->
          <input
            id="quantity"
            v-model="quantityInput"
            type="number"
            :min="packSize"
            :step="packSize"
            :placeholder="String(packSize)"
          />
        </div>

        <button type="submit" :disabled="!canSubmit">
          {{ submitting ? 'Adding…' : 'Add line' }}
        </button>
      </form>

      <p class="hint">{{ packHint }}</p>

      <p v-if="rejection" class="banner banner--error" role="alert">{{ rejection }}</p>

      <table class="lines">
        <thead>
          <tr>
            <th>Product</th>
            <th class="num">Quantity</th>
            <th class="num">Unit price</th>
            <th class="num">Discount</th>
            <th class="num">Line total</th>
            <th><span class="sr-only">Remove</span></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="order.lines.length === 0">
            <td colspan="6" class="empty">
              No lines yet. Add a product above to start the order.
            </td>
          </tr>
          <tr v-for="line in order.lines" :key="line.id">
            <td>{{ line.product_name }}</td>
            <td class="num">{{ line.quantity }}</td>
            <td class="num">{{ money(line.unit_price) }}</td>
            <td class="num" :class="{ discounted: line.discount_rate > 0 }">
              {{ discountLabel(line) }}
            </td>
            <td class="num strong">{{ money(line.line_total) }}</td>
            <td class="num">
              <button
                type="button"
                class="link"
                :disabled="removingLineId === line.id"
                @click="removeLine(line.id)"
              >
                {{ removingLineId === line.id ? 'Removing…' : 'Remove' }}
              </button>
            </td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <td colspan="4" class="num">Order total</td>
            <td class="num total">{{ money(order.order_total) }}</td>
            <td></td>
          </tr>
        </tfoot>
      </table>
    </template>
  </main>
</template>

<style scoped>
.page {
  font-family: system-ui, sans-serif;
  max-width: 860px;
  margin: 2rem auto;
  padding: 0 1rem;
  color: #1c1c1e;
}

h1 {
  margin-bottom: 0.25rem;
  font-size: 1.6rem;
}

.muted {
  color: #6b6b70;
  font-size: 0.9rem;
  margin: 0 0 1.25rem;
}

.pill {
  display: inline-block;
  padding: 0.1rem 0.5rem;
  border-radius: 999px;
  background: #ececf0;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

/* --- add-line form --- */

.add-line {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: flex-end;
  padding: 1rem;
  border: 1px solid #e0e0e5;
  border-radius: 8px;
  background: #fafafc;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.field--grow {
  flex: 1 1 16rem;
}

label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #45454a;
}

select,
input {
  padding: 0.45rem 0.5rem;
  border: 1px solid #c6c6cc;
  border-radius: 6px;
  font: inherit;
  background: #fff;
}

input[type='number'] {
  width: 7rem;
  text-align: right;
}

select:focus,
input:focus {
  outline: 2px solid #3a6ff7;
  outline-offset: 1px;
  border-color: #3a6ff7;
}

button[type='submit'] {
  padding: 0.5rem 1.1rem;
  border: 0;
  border-radius: 6px;
  background: #2a5bd7;
  color: #fff;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}

button[type='submit']:hover:not(:disabled) {
  background: #1f47ab;
}

button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.hint {
  margin: 0.5rem 0 1.25rem;
  font-size: 0.85rem;
  color: #6b6b70;
}

/* --- banners --- */

.banner {
  margin: 0 0 1rem;
  padding: 0.7rem 0.9rem;
  border-radius: 6px;
  font-size: 0.9rem;
}

.banner--error {
  border: 1px solid #e5b4b4;
  background: #fdf3f3;
  color: #8c1c1c;
}

/* --- lines table --- */

.lines {
  width: 100%;
  border-collapse: collapse;
  font-variant-numeric: tabular-nums;
}

.lines th,
.lines td {
  padding: 0.55rem 0.6rem;
  border-bottom: 1px solid #e8e8ed;
  text-align: left;
}

.lines th {
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #6b6b70;
  border-bottom: 2px solid #d8d8de;
}

.num {
  text-align: right;
}

.strong {
  font-weight: 600;
}

.discounted {
  color: #1c7a4a;
  font-weight: 600;
}

.empty {
  padding: 1.75rem 0.6rem;
  text-align: center;
  color: #8a8a90;
  font-style: italic;
}

.lines tfoot td {
  border-bottom: 0;
  border-top: 2px solid #d8d8de;
  padding-top: 0.8rem;
  font-weight: 600;
}

.total {
  font-size: 1.15rem;
}

.link {
  border: 0;
  background: none;
  padding: 0;
  font: inherit;
  color: #a5252f;
  cursor: pointer;
  text-decoration: underline;
}

.link:hover:not(:disabled) {
  color: #7a1b22;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
}
</style>

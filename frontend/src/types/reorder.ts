// Hand-mirrored from the backend's Pydantic response models. There is no
// codegen in this repo — keep these in sync manually with:
//   backend/app/features/customers/schemas.py
//   backend/app/features/reorder/schemas.py
//   backend/app/features/draft/schemas.py

export interface Customer {
  id: number
  name: string
  email: string
}

export interface ReorderSuggestion {
  product_id: number
  name: string
  sku: string
  pack_size: number
  unit_price: number
  last_order_date: string
  cadence_days: number
  next_due_date: string
  days_overdue: number
  suggested_quantity: number
}

export interface DraftLineInput {
  product_id: number
  quantity: number
}

export interface SaveLinesRequest {
  lines: DraftLineInput[]
}

export interface DraftLineOut {
  product_id: number
  name: string
  sku: string
  quantity: number
  unit_price: number
}

export interface DraftOrder {
  id: number
  customer_id: number
  status: 'draft'
  lines: DraftLineOut[]
}

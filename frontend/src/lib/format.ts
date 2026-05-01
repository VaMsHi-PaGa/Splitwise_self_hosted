export function formatCurrency(amount: number | string): string {
  const num = typeof amount === 'string' ? parseFloat(amount) : amount
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
  }).format(num)
}

export function formatDate(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleDateString('en-IN')
}

export const CATEGORIES = [
  'Groceries',
  'Rent',
  'Electricity',
  'WiFi',
  'Maid',
  'Cook',
  'Petrol',
  'Travel',
  'Dining',
  'Subscriptions',
  'Festival',
  'Office Lunch',
  'Other',
]

export const GROUP_CATEGORIES = ['trip', 'flatmates', 'family', 'office', 'friends', 'other']

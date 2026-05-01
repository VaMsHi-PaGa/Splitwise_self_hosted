'use client'

import { useEffect, useState } from 'react'
import { useAuth } from '@/lib/auth'
import { useRouter, useParams } from 'next/navigation'
import { Navbar } from '@/components/Navbar'
import api from '@/lib/api'
import { formatCurrency, formatDate } from '@/lib/format'

interface Expense {
  id: string
  description: string
  amount: number
  category: string
  created_by: string
  created_at: string
}

interface Balance {
  user_id: string
  user_name: string
  balance: number
  is_creditor: boolean
}

export default function GroupDetail() {
  const { isAuthenticated, loading } = useAuth()
  const router = useRouter()
  const params = useParams()
  const groupId = params.id as string

  const [group, setGroup] = useState<any>(null)
  const [expenses, setExpenses] = useState<Expense[]>([])
  const [balances, setBalances] = useState<Balance[]>([])
  const [showAddExpense, setShowAddExpense] = useState(false)
  const [pageLoading, setPageLoading] = useState(true)

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, loading, router])

  useEffect(() => {
    if (isAuthenticated && groupId) {
      fetchGroupData()
    }
  }, [isAuthenticated, groupId])

  const fetchGroupData = async () => {
    try {
      const [groupRes, expenseRes, balanceRes] = await Promise.all([
        api.get(`/groups/${groupId}`),
        api.get(`/groups/${groupId}/expenses`),
        api.get(`/groups/${groupId}/balances`),
      ])
      setGroup(groupRes.data)
      setExpenses(expenseRes.data || [])
      setBalances(balanceRes.data.balances || [])
    } catch (err) {
      console.error('Failed to load group data')
    } finally {
      setPageLoading(false)
    }
  }

  const downloadCSV = async () => {
    try {
      const response = await api.get(`/groups/${groupId}/export.csv`, {
        responseType: 'blob',
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `${group.name}_expenses.csv`)
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    } catch (err) {
      console.error('Failed to download CSV')
    }
  }

  if (!isAuthenticated || pageLoading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold">{group?.name}</h1>
          <div className="flex gap-2">
            <button onClick={() => setShowAddExpense(true)} className="btn btn-primary">
              + Add Expense
            </button>
            <button onClick={downloadCSV} className="btn btn-secondary">
              📥 Export CSV
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {balances.map((balance) => (
            <div key={balance.user_id} className="card">
              <p className="text-gray-600 dark:text-gray-400">{balance.user_name}</p>
              <p className={`text-2xl font-bold ${balance.is_creditor ? 'text-green-500' : 'text-red-500'}`}>
                {balance.is_creditor ? '+' : '-'}{formatCurrency(Math.abs(balance.balance))}
              </p>
            </div>
          ))}
        </div>

        <div className="card">
          <h2 className="text-2xl font-bold mb-4">Recent Expenses</h2>
          {expenses.length > 0 ? (
            <div className="space-y-3">
              {expenses.map((exp) => (
                <div key={exp.id} className="flex justify-between items-center p-4 bg-gray-100 dark:bg-gray-700 rounded">
                  <div>
                    <p className="font-medium">{exp.description}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{formatDate(exp.created_at)}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold">{formatCurrency(exp.amount)}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400 capitalize">{exp.category}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-600">No expenses yet</p>
          )}
        </div>

        {showAddExpense && (
          <div className="modal-overlay" onClick={() => setShowAddExpense(false)}>
            <div className="modal max-w-2xl" onClick={(e) => e.stopPropagation()}>
              <h2 className="text-2xl font-bold mb-4">Add Expense</h2>
              <p className="text-gray-600">Expense form coming soon...</p>
              <button
                onClick={() => setShowAddExpense(false)}
                className="btn btn-primary mt-4"
              >
                Close
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

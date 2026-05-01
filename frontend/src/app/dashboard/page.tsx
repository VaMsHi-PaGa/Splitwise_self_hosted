'use client'

import { useEffect, useState } from 'react'
import { useAuth } from '@/lib/auth'
import { useRouter } from 'next/navigation'
import { Navbar } from '@/components/Navbar'
import api from '@/lib/api'
import { formatCurrency } from '@/lib/format'
import Link from 'next/link'

interface GroupBalance {
  group_id: string
  group_name: string
  balances: Array<{
    user_id: string
    user_name: string
    balance: number
    is_creditor: boolean
  }>
}

export default function Dashboard() {
  const { isAuthenticated, loading } = useAuth()
  const router = useRouter()
  const [data, setData] = useState<any>(null)
  const [error, setError] = useState('')
  const [pageLoading, setPageLoading] = useState(true)

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, loading, router])

  useEffect(() => {
    if (isAuthenticated) {
      fetchBalances()
    }
  }, [isAuthenticated])

  const fetchBalances = async () => {
    try {
      const { data } = await api.get('/balances')
      setData(data)
    } catch (err: any) {
      setError('Failed to load balances')
    } finally {
      setPageLoading(false)
    }
  }

  if (!isAuthenticated || pageLoading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      <div className="max-w-6xl mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold mb-8">Dashboard</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="card">
            <p className="text-gray-600 dark:text-gray-400 mb-2">You Owe</p>
            <p className="text-4xl font-bold text-red-500">
              {formatCurrency(data?.total_owing || 0)}
            </p>
          </div>
          <div className="card">
            <p className="text-gray-600 dark:text-gray-400 mb-2">You Are Owed</p>
            <p className="text-4xl font-bold text-green-500">
              {formatCurrency(data?.total_owed || 0)}
            </p>
          </div>
        </div>

        <div className="space-y-6">
          <h2 className="text-2xl font-bold">Your Groups</h2>
          {data?.groups && data.groups.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {data.groups.map((group: GroupBalance) => (
                <Link key={group.group_id} href={`/groups/${group.group_id}`}>
                  <div className="card hover:shadow-lg cursor-pointer transition-shadow">
                    <h3 className="text-xl font-bold mb-4">{group.group_name}</h3>
                    <div className="space-y-2">
                      {group.balances.map((balance) => (
                        <div key={balance.user_id} className="flex justify-between">
                          <span>{balance.user_name}</span>
                          <span className={balance.is_creditor ? 'text-green-500' : 'text-red-500'}>
                            {balance.is_creditor ? '+' : '-'}{formatCurrency(Math.abs(balance.balance))}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="card text-center">
              <p className="text-gray-600">No groups yet. Create one to get started!</p>
              <Link href="/groups" className="btn btn-primary mt-4 inline-block">
                Create Group
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

'use client'

import { useEffect, useState } from 'react'
import { useAuth } from '@/lib/auth'
import { useRouter } from 'next/navigation'
import { Navbar } from '@/components/Navbar'
import api from '@/lib/api'
import Link from 'next/link'
import { GROUP_CATEGORIES } from '@/lib/format'

interface Group {
  id: string
  name: string
  category: string
  created_at: string
}

export default function Groups() {
  const { isAuthenticated, loading } = useAuth()
  const router = useRouter()
  const [groups, setGroups] = useState<Group[]>([])
  const [showModal, setShowModal] = useState(false)
  const [formData, setFormData] = useState({ name: '', category: 'other', member_emails: [] })
  const [pageLoading, setPageLoading] = useState(true)

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, loading, router])

  useEffect(() => {
    if (isAuthenticated) {
      fetchGroups()
    }
  }, [isAuthenticated])

  const fetchGroups = async () => {
    try {
      const { data } = await api.get('/groups')
      setGroups(data)
    } catch (err) {
      console.error('Failed to load groups')
    } finally {
      setPageLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await api.post('/groups', formData)
      setFormData({ name: '', category: 'other', member_emails: [] })
      setShowModal(false)
      fetchGroups()
    } catch (err) {
      console.error('Failed to create group')
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
          <h1 className="text-4xl font-bold">Groups</h1>
          <button onClick={() => setShowModal(true)} className="btn btn-primary">
            + Create Group
          </button>
        </div>

        {groups.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {groups.map((group) => (
              <Link key={group.id} href={`/groups/${group.id}`}>
                <div className="card hover:shadow-lg cursor-pointer transition-shadow">
                  <h3 className="text-xl font-bold mb-2">{group.name}</h3>
                  <p className="text-gray-600 dark:text-gray-400 capitalize">{group.category}</p>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className="card text-center">
            <p className="text-gray-600">No groups yet. Create one to get started!</p>
          </div>
        )}

        {showModal && (
          <div className="modal-overlay" onClick={() => setShowModal(false)}>
            <div className="modal" onClick={(e) => e.stopPropagation()}>
              <h2 className="text-2xl font-bold mb-4">Create Group</h2>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Group Name</label>
                  <input
                    type="text"
                    className="input"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Category</label>
                  <select
                    className="input"
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  >
                    {GROUP_CATEGORIES.map((cat) => (
                      <option key={cat} value={cat}>
                        {cat.charAt(0).toUpperCase() + cat.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="flex gap-2">
                  <button type="submit" className="btn btn-primary flex-1">
                    Create
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowModal(false)}
                    className="btn btn-secondary flex-1"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

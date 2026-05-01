'use client'

import { useEffect, useState } from 'react'
import { useAuth } from '@/lib/auth'
import { useRouter } from 'next/navigation'
import { Navbar } from '@/components/Navbar'

export default function Settings() {
  const { user, isAuthenticated, loading } = useAuth()
  const router = useRouter()
  const [formData, setFormData] = useState({ name: '', phone: '', upi_id: '' })

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, loading, router])

  useEffect(() => {
    if (user) {
      setFormData({
        name: user.name || '',
        phone: user.phone || '',
        upi_id: user.upi_id || '',
      })
    }
  }, [user])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    // Profile update would be implemented here
    console.log('Profile update:', formData)
  }

  if (!isAuthenticated) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      <div className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold mb-8">Settings</h1>

        <div className="card">
          <h2 className="text-2xl font-bold mb-6">Profile</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Name</label>
              <input
                type="text"
                className="input"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Phone</label>
              <input
                type="tel"
                className="input"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">UPI ID</label>
              <input
                type="text"
                className="input"
                value={formData.upi_id}
                onChange={(e) => setFormData({ ...formData, upi_id: e.target.value })}
                placeholder="yourname@upi"
              />
            </div>
            <button type="submit" className="btn btn-primary">
              Save Changes
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

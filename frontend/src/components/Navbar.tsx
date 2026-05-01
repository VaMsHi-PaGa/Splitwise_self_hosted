'use client'

import Link from 'next/link'
import { useAuth } from '@/lib/auth'
import { useRouter } from 'next/navigation'
import { useTheme } from 'next-themes'
import { useEffect, useState } from 'react'

export function Navbar() {
  const { user, logout, isAuthenticated } = useAuth()
  const router = useRouter()
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => setMounted(true), [])

  const handleLogout = () => {
    logout()
    router.push('/login')
  }

  if (!isAuthenticated) return null

  return (
    <nav className="bg-white dark:bg-gray-800 shadow">
      <div className="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
        <Link href="/dashboard" className="text-2xl font-bold text-blue-500">
          SplitSmart
        </Link>
        <div className="flex gap-4 items-center">
          <Link href="/dashboard" className="hover:text-blue-500">
            Dashboard
          </Link>
          <Link href="/groups" className="hover:text-blue-500">
            Groups
          </Link>
          <Link href="/settings" className="hover:text-blue-500">
            Settings
          </Link>
          {mounted && (
            <button
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              className="p-2 rounded bg-gray-200 dark:bg-gray-700"
            >
              {theme === 'dark' ? '☀️' : '🌙'}
            </button>
          )}
          <span className="text-sm">{user?.name}</span>
          <button onClick={handleLogout} className="btn btn-secondary btn-sm">
            Logout
          </button>
        </div>
      </div>
    </nav>
  )
}

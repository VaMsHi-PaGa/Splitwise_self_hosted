import type { Metadata } from 'next'
import { AuthProvider } from '@/lib/auth'
import { ThemeProviderWrapper } from '@/lib/theme'
import '@/styles/globals.css'

export const metadata: Metadata = {
  title: 'SplitSmart India',
  description: 'Smart expense sharing for Indian groups',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProviderWrapper>
          <AuthProvider>
            {children}
          </AuthProvider>
        </ThemeProviderWrapper>
      </body>
    </html>
  )
}

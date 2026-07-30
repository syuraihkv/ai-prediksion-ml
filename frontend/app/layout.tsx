import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Link from 'next/link'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AI Market Prediction',
  description: 'AI-powered market prediction and analysis platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <nav className="bg-dark-900 border-b border-gray-700">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center">
                <Link href="/" className="text-white font-bold text-xl">
                  🤖 AI Market Prediction
                </Link>
              </div>
              <div className="hidden md:block">
                <div className="ml-10 flex items-baseline space-x-4">
                  <Link href="/" className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium">
                    Home
                  </Link>
                  <Link href="/market" className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium">
                    Live Market
                  </Link>
                  <Link href="/prediction" className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium">
                    AI Prediction
                  </Link>
                  <Link href="/models" className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium">
                    Compare Models
                  </Link>
                  <Link href="/performance" className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium">
                    Performance
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </nav>
        <main className="min-h-screen">
          {children}
        </main>
        <footer className="bg-dark-900 border-t border-gray-700 mt-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <p className="text-center text-gray-400 text-sm">
              © 2024 AI Market Prediction. Powered by Machine Learning.
            </p>
          </div>
        </footer>
      </body>
    </html>
  )
}

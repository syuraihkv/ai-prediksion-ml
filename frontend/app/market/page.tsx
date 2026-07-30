'use client'

import { useEffect, useState } from 'react'
import { TrendingUp, TrendingDown, Activity } from 'lucide-react'

interface MarketData {
  asset: string
  price: number
  change_24h: number
  volume_24h: number
  high_24h: number
  low_24h: number
}

export default function MarketPage() {
  const [selectedAsset, setSelectedAsset] = useState('BTC')
  const [marketData, setMarketData] = useState<MarketData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchMarketData(selectedAsset)
  }, [selectedAsset])

  const fetchMarketData = async (asset: string) => {
    setLoading(true)
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/market/price/${asset}`)
      const data = await response.json()
      setMarketData(data)
    } catch (error) {
      console.error('Error fetching market data:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-3xl font-bold text-white mb-8">Live Market Data</h1>
      
      {/* Asset Selector */}
      <div className="flex gap-4 mb-8">
        {['BTC', 'ETH', 'XAU'].map((asset) => (
          <button
            key={asset}
            onClick={() => setSelectedAsset(asset)}
            className={`px-6 py-3 rounded-lg font-medium transition-colors ${
              selectedAsset === asset
                ? 'bg-primary-600 text-white'
                : 'bg-dark-700 text-gray-300 hover:bg-dark-600'
            }`}
          >
            {asset}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="text-center text-gray-400 py-12">Loading market data...</div>
      ) : marketData ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Price Card */}
          <div className="bg-dark-800 p-6 rounded-lg border border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold text-white">{marketData.asset}</h2>
              <div className={`flex items-center gap-2 ${marketData.change_24h >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {marketData.change_24h >= 0 ? <TrendingUp /> : <TrendingDown />}
                <span className="font-semibold">{marketData.change_24h.toFixed(2)}%</span>
              </div>
            </div>
            <div className="text-4xl font-bold text-white mb-4">
              ${marketData.price.toLocaleString()}
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-400">24h High:</span>
                <span className="text-white ml-2">${marketData.high_24h.toLocaleString()}</span>
              </div>
              <div>
                <span className="text-gray-400">24h Low:</span>
                <span className="text-white ml-2">${marketData.low_24h.toLocaleString()}</span>
              </div>
              <div>
                <span className="text-gray-400">24h Volume:</span>
                <span className="text-white ml-2">${(marketData.volume_24h / 1e9).toFixed(2)}B</span>
              </div>
            </div>
          </div>

          {/* Activity Indicator */}
          <div className="bg-dark-800 p-6 rounded-lg border border-gray-700">
            <div className="flex items-center gap-3 mb-4">
              <Activity className="text-primary-400" />
              <h3 className="text-xl font-semibold text-white">Market Activity</h3>
            </div>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Status</span>
                <span className="text-green-400 font-medium">Active</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Last Update</span>
                <span className="text-white">Just now</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Data Source</span>
                <span className="text-white">yfinance</span>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center text-gray-400 py-12">No data available</div>
      )}
    </div>
  )
}

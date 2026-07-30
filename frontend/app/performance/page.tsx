'use client'

import { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function PerformancePage() {
  const [selectedAsset, setSelectedAsset] = useState('BTC')
  
  // Mock performance data (in production, fetch from API)
  const performanceData = [
    { date: '2024-01', accuracy: 0.48 },
    { date: '2024-02', accuracy: 0.51 },
    { date: '2024-03', accuracy: 0.49 },
    { date: '2024-04', accuracy: 0.53 },
    { date: '2024-05', accuracy: 0.52 },
    { date: '2024-06', accuracy: 0.54 },
    { date: '2024-07', accuracy: 0.52 },
  ]

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-3xl font-bold text-white mb-8">Model Performance</h1>
      
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

      {/* Performance Chart */}
      <div className="bg-dark-800 p-6 rounded-lg border border-gray-700 mb-8">
        <h2 className="text-xl font-semibold text-white mb-4">Accuracy Over Time</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={performanceData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="date" stroke="#9ca3af" />
            <YAxis stroke="#9ca3af" />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
              itemStyle={{ color: '#fff' }}
            />
            <Line type="monotone" dataKey="accuracy" stroke="#0ea5e9" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricCard 
          title="Overall Accuracy" 
          value="52.3%" 
          change="+2.1%" 
          positive={true}
        />
        <MetricCard 
          title="Precision" 
          value="53.1%" 
          change="+1.8%" 
          positive={true}
        />
        <MetricCard 
          title="Recall" 
          value="51.9%" 
          change="+0.5%" 
          positive={true}
        />
      </div>

      {/* Info Box */}
      <div className="mt-8 bg-dark-800 p-6 rounded-lg border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-2">About Performance Metrics</h3>
        <p className="text-gray-400 text-sm">
          Performance metrics are calculated based on historical predictions and actual market movements. 
          The model is continuously retrained with new data to improve accuracy over time.
        </p>
      </div>
    </div>
  )
}

function MetricCard({ title, value, change, positive }: { title: string, value: string, change: string, positive: boolean }) {
  return (
    <div className="bg-dark-800 p-6 rounded-lg border border-gray-700">
      <h3 className="text-sm text-gray-400 mb-2">{title}</h3>
      <div className="text-3xl font-bold text-white mb-2">{value}</div>
      <div className={`text-sm ${positive ? 'text-green-400' : 'text-red-400'}`}>
        {change} from last month
      </div>
    </div>
  )
}

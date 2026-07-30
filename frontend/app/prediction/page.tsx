'use client'

import { useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { Brain, TrendingUp, TrendingDown, Minus } from 'lucide-react'

interface PredictionData {
  asset: string
  prediction: string
  confidence: number
  probability_up: number
  probability_down: number
  model_used: string
  features: Record<string, number>
  timestamp: string
  is_ml_backed: boolean
}

export default function PredictionPage() {
  const searchParams = useSearchParams()
  const [selectedAsset, setSelectedAsset] = useState(searchParams.get('asset') || 'BTC')
  const [prediction, setPrediction] = useState<PredictionData | null>(null)
  const [loading, setLoading] = useState(false)

  const getPrediction = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/prediction/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ asset: selectedAsset })
      })
      const data = await response.json()
      setPrediction(data)
    } catch (error) {
      console.error('Error getting prediction:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    getPrediction()
  }, [selectedAsset])

  const getPredictionIcon = (pred: string) => {
    switch (pred) {
      case 'BUY': return <TrendingUp className="w-12 h-12 text-green-400" />
      case 'SELL': return <TrendingDown className="w-12 h-12 text-red-400" />
      default: return <Minus className="w-12 h-12 text-yellow-400" />
    }
  }

  const getPredictionColor = (pred: string) => {
    switch (pred) {
      case 'BUY': return 'bg-green-500/20 border-green-500'
      case 'SELL': return 'bg-red-500/20 border-red-500'
      default: return 'bg-yellow-500/20 border-yellow-500'
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-3xl font-bold text-white mb-8">AI Prediction</h1>
      
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
        <button
          onClick={getPrediction}
          disabled={loading}
          className="px-6 py-3 rounded-lg font-medium bg-dark-700 text-gray-300 hover:bg-dark-600 disabled:opacity-50"
        >
          {loading ? 'Loading...' : 'Refresh'}
        </button>
      </div>

      {loading ? (
        <div className="text-center text-gray-400 py-12">Generating prediction...</div>
      ) : prediction ? (
        <div className="space-y-8">
          {/* Prediction Card */}
          <div className={`p-8 rounded-lg border-2 ${getPredictionColor(prediction.prediction)}`}>
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-white">{prediction.asset}</h2>
                <p className="text-gray-400">AI-powered prediction</p>
              </div>
              {getPredictionIcon(prediction.prediction)}
            </div>
            
            <div className="text-center mb-6">
              <div className="text-5xl font-bold text-white mb-2">{prediction.prediction}</div>
              <div className="text-xl text-gray-300">Confidence: {(prediction.confidence * 100).toFixed(1)}%</div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="bg-dark-900 p-4 rounded-lg">
                <div className="text-sm text-gray-400 mb-1">Probability Up</div>
                <div className="text-2xl font-bold text-green-400">{(prediction.probability_up * 100).toFixed(1)}%</div>
              </div>
              <div className="bg-dark-900 p-4 rounded-lg">
                <div className="text-sm text-gray-400 mb-1">Probability Down</div>
                <div className="text-2xl font-bold text-red-400">{(prediction.probability_down * 100).toFixed(1)}%</div>
              </div>
            </div>

            <div className="mt-6 pt-6 border-t border-gray-700">
              <div className="flex items-center gap-2 text-sm text-gray-400">
                <Brain className="w-4 h-4" />
                <span>Model: {prediction.model_used}</span>
                {prediction.is_ml_backed && <span className="text-green-400">• ML-backed</span>}
              </div>
            </div>
          </div>

          {/* Features */}
          <div className="bg-dark-800 p-6 rounded-lg border border-gray-700">
            <h3 className="text-xl font-semibold text-white mb-4">Feature Analysis</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(prediction.features).map(([key, value]) => (
                <div key={key} className="bg-dark-900 p-4 rounded-lg">
                  <div className="text-sm text-gray-400 mb-1">{key}</div>
                  <div className="text-lg font-semibold text-white">{value.toFixed(3)}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center text-gray-400 py-12">No prediction available</div>
      )}
    </div>
  )
}

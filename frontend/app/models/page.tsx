'use client'

import { useEffect, useState } from 'react'
import { Brain, BarChart3, Trophy } from 'lucide-react'

interface ModelInfo {
  name: string
  type: string
  accuracy: number
  precision: number
  recall: number
  f1_score: number
  roc_auc: number
}

interface ModelComparison {
  asset: string
  models: ModelInfo[]
  best_model: string
  timestamp: string
}

export default function ModelsPage() {
  const [selectedAsset, setSelectedAsset] = useState('BTC')
  const [comparison, setComparison] = useState<ModelComparison | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchComparison(selectedAsset)
  }, [selectedAsset])

  const fetchComparison = async (asset: string) => {
    setLoading(true)
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/models/compare/${asset}`)
      const data = await response.json()
      setComparison(data)
    } catch (error) {
      console.error('Error fetching model comparison:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-3xl font-bold text-white mb-8">Model Comparison</h1>
      
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
        <div className="text-center text-gray-400 py-12">Loading model comparison...</div>
      ) : comparison ? (
        <div className="space-y-8">
          {/* Best Model Card */}
          <div className="bg-gradient-to-r from-primary-600/20 to-primary-800/20 p-6 rounded-lg border border-primary-500">
            <div className="flex items-center gap-3 mb-4">
              <Trophy className="w-8 h-8 text-primary-400" />
              <h2 className="text-2xl font-bold text-white">Best Model</h2>
            </div>
            <div className="text-3xl font-bold text-white mb-2">{comparison.best_model}</div>
            <div className="text-gray-300">Selected based on highest accuracy score</div>
          </div>

          {/* Model Comparison Table */}
          <div className="bg-dark-800 rounded-lg border border-gray-700 overflow-hidden">
            <div className="p-6 border-b border-gray-700">
              <h3 className="text-xl font-semibold text-white flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                Performance Metrics
              </h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-dark-900">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Model</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Type</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Accuracy</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Precision</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Recall</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">F1 Score</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">ROC AUC</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-700">
                  {comparison.models.map((model) => (
                    <tr 
                      key={model.name}
                      className={model.name === comparison.best_model ? 'bg-primary-900/20' : ''}
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <Brain className={`w-4 h-4 mr-2 ${model.name === comparison.best_model ? 'text-primary-400' : 'text-gray-400'}`} />
                          <span className="text-white font-medium">{model.name}</span>
                          {model.name === comparison.best_model && (
                            <span className="ml-2 text-xs bg-primary-600 text-white px-2 py-1 rounded">Best</span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-400">{model.type}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`font-semibold ${model.accuracy > 0.5 ? 'text-green-400' : 'text-red-400'}`}>
                          {(model.accuracy * 100).toFixed(1)}%
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-300">{(model.precision * 100).toFixed(1)}%</td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-300">{(model.recall * 100).toFixed(1)}%</td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-300">{(model.f1_score * 100).toFixed(1)}%</td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-300">{(model.roc_auc * 100).toFixed(1)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center text-gray-400 py-12">No comparison data available</div>
      )}
    </div>
  )
}

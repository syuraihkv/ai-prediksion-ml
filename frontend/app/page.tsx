import Link from 'next/link'
import { TrendingUp, Brain, BarChart3, Zap } from 'lucide-react'

export default function Home() {
  return (
    <div className="relative overflow-hidden">
      {/* Hero Section */}
      <div className="relative bg-gradient-to-b from-dark-900 to-dark-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
              AI-Powered Market Prediction
            </h1>
            <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
              Leverage machine learning to predict market movements with confidence. 
              Compare multiple models, analyze performance metrics, and make data-driven decisions.
            </p>
            <div className="flex justify-center gap-4">
              <Link
                href="/prediction"
                className="bg-primary-600 hover:bg-primary-700 text-white font-bold py-3 px-8 rounded-lg transition-colors"
              >
                Get Prediction
              </Link>
              <Link
                href="/market"
                className="bg-dark-700 hover:bg-dark-600 text-white font-bold py-3 px-8 rounded-lg border border-gray-600 transition-colors"
              >
                View Market
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-3xl font-bold text-white text-center mb-12">
          Powerful Features
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          <FeatureCard
            icon={<TrendingUp className="w-8 h-8" />}
            title="Real-Time Data"
            description="Live market data from multiple sources including CoinGecko and yfinance"
          />
          <FeatureCard
            icon={<Brain className="w-8 h-8" />}
            title="AI Predictions"
            description="Machine learning models trained on historical data for accurate predictions"
          />
          <FeatureCard
            icon={<BarChart3 className="w-8 h-8" />}
            title="Model Comparison"
            description="Compare performance across multiple ML algorithms simultaneously"
          />
          <FeatureCard
            icon={<Zap className="w-8 h-8" />}
            title="Fast & Reliable"
            description="Built with Next.js and FastAPI for optimal performance"
          />
        </div>
      </div>

      {/* Supported Assets */}
      <div className="bg-dark-800 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-white text-center mb-8">
            Supported Assets
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <AssetCard symbol="BTC" name="Bitcoin" type="Crypto" />
            <AssetCard symbol="ETH" name="Ethereum" type="Crypto" />
            <AssetCard symbol="XAU" name="Gold" type="Commodity" />
          </div>
        </div>
      </div>
    </div>
  )
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <div className="bg-dark-700 p-6 rounded-lg border border-gray-600 hover:border-primary-500 transition-colors">
      <div className="text-primary-400 mb-4">{icon}</div>
      <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
      <p className="text-gray-400">{description}</p>
    </div>
  )
}

function AssetCard({ symbol, name, type }: { symbol: string, name: string, type: string }) {
  return (
    <div className="bg-dark-900 p-6 rounded-lg border border-gray-600 hover:border-primary-500 transition-colors">
      <div className="flex items-center justify-between mb-4">
        <span className="text-2xl font-bold text-white">{symbol}</span>
        <span className="text-sm text-gray-400 bg-dark-700 px-3 py-1 rounded-full">{type}</span>
      </div>
      <h3 className="text-lg font-semibold text-white">{name}</h3>
      <Link
        href={`/prediction?asset=${symbol}`}
        className="mt-4 inline-block text-primary-400 hover:text-primary-300 text-sm font-medium"
      >
        Get Prediction →
      </Link>
    </div>
  )
}

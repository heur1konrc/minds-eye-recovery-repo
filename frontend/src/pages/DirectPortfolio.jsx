import React, { useState, useEffect } from 'react'

const DirectPortfolio = () => {
  const [images, setImages] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    console.log('🚀 DirectPortfolio component mounted')
    fetchImages()
  }, [])

  const fetchImages = async () => {
    try {
      console.log('📡 Fetching from /api/simple-portfolio...')
      const response = await fetch('/api/simple-portfolio')
      console.log('📊 Response:', response.status, response.statusText)
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      
      const data = await response.json()
      console.log('✅ Data received:', data)
      
      // Filter out images that are set as About images
      const portfolioImages = data.filter(image => !image.is_about)
      console.log('📈 Portfolio image count (excluding About images):', portfolioImages.length)
      console.log('🚫 About images excluded:', data.length - portfolioImages.length)
      
      setImages(portfolioImages)
      setLoading(false)
    } catch (err) {
      console.error('❌ Fetch error:', err)
      setError(err.message)
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center pt-20">
        <div className="text-white text-xl">Loading portfolio...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center pt-20">
        <div className="text-red-400 text-xl">Error: {error}</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-900 pt-20">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-4">Portfolio</h1>
          <p className="text-gray-300">
            Explore my collection of {images.length} professional photographs
          </p>
        </div>

        {images.length === 0 ? (
          <div className="text-center text-gray-400">
            <p>No images available in the portfolio</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {images.map((image, index) => (
              <div key={image.id || index} className="bg-gray-800 rounded-lg overflow-hidden shadow-lg">
                <div className="aspect-square bg-gray-700 flex items-center justify-center">
                  <img
                    src={`/static/assets/${image.filename}`}
                    alt={image.title || `Image ${index + 1}`}
                    className="w-full h-full object-cover"
                    onLoad={() => console.log(`✅ Image loaded: ${image.filename}`)}
                    onError={(e) => {
                      console.error(`❌ Image failed to load: ${image.filename}`)
                      e.target.src = '/static/logo.png' // Fallback image
                    }}
                  />
                </div>
                <div className="p-4">
                  <h3 className="text-white font-semibold mb-2">
                    {image.title || `Image ${index + 1}`}
                  </h3>
                  {image.description && (
                    <p className="text-gray-400 text-sm">{image.description}</p>
                  )}
                  {image.categories && image.categories.length > 0 && (
                    <div className="mt-2">
                      {image.categories.map((category, catIndex) => (
                        <span
                          key={catIndex}
                          className="inline-block bg-orange-500 text-white text-xs px-2 py-1 rounded mr-2 mb-1"
                        >
                          {category}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default DirectPortfolio


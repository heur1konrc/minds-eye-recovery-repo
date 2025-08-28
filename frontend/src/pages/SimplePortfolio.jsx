import React, { useState, useEffect } from 'react'

const SimplePortfolio = () => {
  const [images, setImages] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simple fetch - just get the data and display it
    fetch('/api/simple-portfolio')
      .then(response => response.json())
      .then(data => {
        console.log('Got data:', data)
        // Filter out images that are set as About images
        const portfolioImages = data.filter(image => !image.is_about)
        console.log('Portfolio images (excluding About):', portfolioImages.length)
        setImages(portfolioImages)
        setLoading(false)
      })
      .catch(error => {
        console.error('Error:', error)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading portfolio...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-900 py-20">
      <div className="container mx-auto px-4">
        <h1 className="text-4xl font-bold text-orange-500 text-center mb-4">Portfolio</h1>
        <p className="text-slate-300 text-center mb-12">
          Explore my collection of {images.length} professional photographs
        </p>

        {/* Simple Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {images.map((image) => (
            <div key={image.id} className="bg-white rounded-lg overflow-hidden shadow-lg">
              <img
                src={image.url}
                alt={image.title}
                className="w-full h-64 object-cover"
                onError={(e) => {
                  console.log('Image failed to load:', image.url)
                  e.target.src = 'https://via.placeholder.com/300x200?text=Image+Not+Found'
                }}
              />
              <div className="p-4">
                <h3 className="font-semibold text-slate-900">{image.title}</h3>
                <p className="text-slate-600 text-sm">{image.description}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Debug Info */}
        <div className="mt-12 p-4 bg-slate-800 rounded-lg">
          <h3 className="text-white font-bold mb-2">Debug Info:</h3>
          <p className="text-slate-300">Total images loaded: {images.length}</p>
          {images.length > 0 && (
            <div className="mt-2">
              <p className="text-slate-300">First image URL: {images[0].url}</p>
              <p className="text-slate-300">First image filename: {images[0].filename}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default SimplePortfolio


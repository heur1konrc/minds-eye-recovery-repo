import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Grid, List, Search } from 'lucide-react'
import { Button } from '@/components/ui/button'

const PortfolioPage = () => {
  const [images, setImages] = useState([])
  const [categories, setCategories] = useState([])
  const [selectedCategory, setSelectedCategory] = useState('All Work')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [viewMode, setViewMode] = useState('grid')
  const [searchTerm, setSearchTerm] = useState('')

  // Fetch portfolio data
  useEffect(() => {
    const fetchPortfolio = async () => {
      try {
        setLoading(true)
        const response = await fetch('/api/simple-portfolio')
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const data = await response.json()
        console.log('Portfolio data loaded:', data)
        
        setImages(data)
        
        // Extract unique categories
        const allCategories = data.flatMap(img => img.categories || [])
        const uniqueCategories = ['All Work', 'Landscapes', 'Wildlife', 'Portraits', 'Events', ...new Set(allCategories)]
        setCategories([...new Set(uniqueCategories)])
        
      } catch (err) {
        console.error('Error loading portfolio:', err)
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchPortfolio()
  }, [])

  // Filter images by category and search term
  const filteredImages = images.filter(img => {
    const matchesCategory = selectedCategory === 'All Work' || img.categories?.includes(selectedCategory)
    const matchesSearch = !searchTerm || 
      img.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      img.description?.toLowerCase().includes(searchTerm.toLowerCase())
    return matchesCategory && matchesSearch
  })

  return (
    <div className="min-h-screen bg-slate-50 pt-20">
      {/* Header */}
      <div className="bg-slate-900 text-white py-16">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <motion.h1 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-4xl md:text-5xl font-bold mb-4 text-orange-400"
          >
            Portfolio - TEST DEPLOYMENT
          </motion.h1>
          <motion.p 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-xl text-slate-300"
          >
            Explore my collection of {images.length} professional photographs
          </motion.p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Filters and Controls */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <div className="flex flex-col lg:flex-row gap-6 items-start lg:items-center justify-between">
            {/* Category Filters */}
            <div className="flex flex-wrap gap-2">
              {categories.map(category => (
                <Button
                  key={category}
                  variant={selectedCategory === category ? "default" : "outline"}
                  size="sm"
                  onClick={() => setSelectedCategory(category)}
                  className={`text-sm ${
                    selectedCategory === category 
                      ? 'bg-orange-500 hover:bg-orange-600 text-white' 
                      : 'border-orange-500 text-orange-500 hover:bg-orange-500 hover:text-white'
                  }`}
                >
                  {category}
                </Button>
              ))}
            </div>
            
            {/* Search and View Controls */}
            <div className="flex items-center gap-4">
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search images..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                />
              </div>
              
              {/* View Mode Toggle */}
              <div className="flex items-center gap-2">
                <Button
                  variant={viewMode === 'grid' ? "default" : "outline"}
                  size="sm"
                  onClick={() => setViewMode('grid')}
                  className={viewMode === 'grid' ? 'bg-orange-500 hover:bg-orange-600' : 'border-orange-500 text-orange-500 hover:bg-orange-500 hover:text-white'}
                >
                  <Grid className="h-4 w-4" />
                </Button>
                <Button
                  variant={viewMode === 'list' ? "default" : "outline"}
                  size="sm"
                  onClick={() => setViewMode('list')}
                  className={viewMode === 'list' ? 'bg-orange-500 hover:bg-orange-600' : 'border-orange-500 text-orange-500 hover:bg-orange-500 hover:text-white'}
                >
                  <List className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Portfolio Grid */}
        {loading ? (
          <div className="text-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto mb-4"></div>
            <p className="text-slate-600">Loading portfolio...</p>
          </div>
        ) : error ? (
          <div className="text-center py-20">
            <p className="text-red-600 mb-4">Error loading portfolio: {error}</p>
            <Button 
              onClick={() => window.location.reload()}
              className="bg-orange-500 hover:bg-orange-600"
            >
              Try Again
            </Button>
          </div>
        ) : filteredImages.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-slate-500 text-lg">
              {searchTerm ? `No images found for "${searchTerm}"` : `No images found in "${selectedCategory}"`}
            </p>
          </div>
        ) : (
          <motion.div 
            layout
            className={`grid gap-6 ${
              viewMode === 'grid' 
                ? 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4' 
                : 'grid-cols-1 lg:grid-cols-2'
            }`}
          >
            <AnimatePresence>
              {filteredImages.map((image, index) => (
                <motion.div
                  key={image.id}
                  layout
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
                  className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-all duration-300 group"
                >
                  <div className="aspect-square bg-slate-200 relative overflow-hidden">
                    <img
                      src={image.url || `/data/${image.filename}`}
                      alt={image.title}
                      className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                      loading="lazy"
                    />
                    <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors duration-300" />
                  </div>
                  
                  <div className="p-4">
                    <h3 className="font-semibold text-slate-900 mb-2">{image.title}</h3>
                    {image.description && (
                      <p className="text-slate-600 text-sm mb-3 line-clamp-2">{image.description}</p>
                    )}
                    <div className="flex flex-wrap gap-1">
                      {image.categories?.map(cat => (
                        <span
                          key={cat}
                          className="px-2 py-1 bg-orange-100 text-orange-700 text-xs rounded-full"
                        >
                          {cat}
                        </span>
                      ))}
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </motion.div>
        )}
      </div>
    </div>
  )
}

export default PortfolioPage


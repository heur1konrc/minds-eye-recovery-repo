import React, { useState, useEffect, useMemo } from 'react';

const SQLPortfolio = () => {
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [currentPage, setCurrentPage] = useState(1);
  const imagesPerPage = 12;

  // Initialize from URL parameters
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const categoryParam = urlParams.get('category');
    const pageParam = urlParams.get('page');
    
    if (categoryParam) {
      setSelectedCategory(categoryParam);
    }
    if (pageParam) {
      setCurrentPage(parseInt(pageParam) || 1);
    }
  }, []);

  // Update URL when category or page changes
  const updateURL = (category, page) => {
    const url = new URL(window.location);
    if (category && category !== 'All') {
      url.searchParams.set('category', category);
    } else {
      url.searchParams.delete('category');
    }
    if (page && page > 1) {
      url.searchParams.set('page', page);
    } else {
      url.searchParams.delete('page');
    }
    window.history.pushState({}, '', url);
  };

  useEffect(() => {
    fetchImages();
  }, []);

  // Reset pagination when category changes and update URL
  useEffect(() => {
    if (currentPage !== 1) {
      setCurrentPage(1);
      updateURL(selectedCategory, 1);
    } else {
      updateURL(selectedCategory, currentPage);
    }
  }, [selectedCategory]);

  // Update URL when page changes
  useEffect(() => {
    updateURL(selectedCategory, currentPage);
  }, [currentPage]);

  const fetchImages = async () => {
    try {
      console.log('🔍 Fetching images from /api/simple-portfolio...');
      const response = await fetch('/api/simple-portfolio');
      console.log('📡 Response status:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('📊 API Response data:', data);
      console.log('📈 Number of images received:', data.length);
      
      // Filter out images that are set as About images
      const portfolioImages = data.filter(image => !image.is_about);
      console.log('🚫 About images excluded:', data.length - portfolioImages.length);
      console.log('📈 Portfolio images (excluding About):', portfolioImages.length);
      
      setImages(portfolioImages);
      setLoading(false);
      
      console.log('✅ Images set in state:', portfolioImages.length);
    } catch (error) {
      console.error('❌ Error fetching images:', error);
      setLoading(false);
    }
  };

  const getCategories = () => {
    const allCategories = images.flatMap(image => image.categories || []);
    const uniqueCategories = [...new Set(allCategories)];
    return ['All', ...uniqueCategories.sort()];
  };

  const getFilteredImages = () => {
    if (selectedCategory === 'All') {
      return images;
    }
    return images.filter(image => 
      image.categories && image.categories.includes(selectedCategory)
    );
  };

  const getCurrentPageImages = () => {
    const filteredImages = getFilteredImages();
    const startIndex = (currentPage - 1) * imagesPerPage;
    const endIndex = startIndex + imagesPerPage;
    return filteredImages.slice(startIndex, endIndex);
  };

  const getTotalPages = () => {
    const filteredImages = getFilteredImages();
    return Math.ceil(filteredImages.length / imagesPerPage);
  };

  const cleanTitle = (title) => {
    // Remove hex codes from titles - more comprehensive patterns
    return title
      .replace(/\s+[A-F0-9]{6,8}$/i, '')
      .replace(/\s+[A-F0-9]{8}$/i, '')
      .replace(/\s+[A-F0-9]{6}$/i, '')
      .replace(/\s[A-F0-9]{6,8}$/i, '')
      .replace(/[A-F0-9]{6,8}$/i, '')
      .trim();
  };

  const cleanDescription = (description) => {
    if (!description) return '';
    // Clean descriptions too
    return description
      .replace(/\s+[A-F0-9]{6,8}$/i, '')
      .replace(/\s+[A-F0-9]{8}$/i, '')
      .replace(/\s+[A-F0-9]{6}$/i, '')
      .replace(/\s[A-F0-9]{6,8}$/i, '')
      .replace(/[A-F0-9]{6,8}$/i, '')
      .trim();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-800 pt-20 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
      </div>
    );
  }

  const categories = getCategories();
  
  // Use useMemo to ensure proper recalculation when dependencies change
  const filteredImages = useMemo(() => getFilteredImages(), [images, selectedCategory]);
  const currentImages = useMemo(() => {
    const startIndex = (currentPage - 1) * imagesPerPage;
    const endIndex = startIndex + imagesPerPage;
    return filteredImages.slice(startIndex, endIndex);
  }, [filteredImages, currentPage, imagesPerPage]);
  const totalPages = useMemo(() => Math.ceil(filteredImages.length / imagesPerPage), [filteredImages.length, imagesPerPage]);
  const filteredCount = filteredImages.length;

  return (
    <div className="min-h-screen bg-slate-900 pt-20">
      {/* Header */}
      <div className="bg-slate-900 border-b border-slate-700">
        <div className="max-w-6xl mx-auto px-6 py-12 text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Portfolio
          </h1>
          <p className="text-xl text-slate-300 max-w-2xl mx-auto">
            Explore my collection of {images.length} professional photographs
          </p>
        </div>
      </div>

      {/* Category Filter Buttons */}
      <div className="bg-slate-900 border-t border-slate-700">
        <div className="max-w-6xl mx-auto px-6 py-6">
          <div className="flex flex-wrap justify-center gap-4">
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => {
                  setSelectedCategory(category);
                  setCurrentPage(1);
                }}
                className={`px-6 py-3 rounded-full font-medium transition-all duration-300 ${
                  selectedCategory === category
                    ? 'bg-orange-500 text-white shadow-lg'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600 hover:text-white'
                }`}
              >
                {category} ({category === 'All' ? images.length : images.filter(img => img.categories && img.categories.includes(category)).length})
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Results Info */}
      <div className="bg-slate-900 px-6 py-4">
        <div className="max-w-6xl mx-auto">
          <p className="text-slate-400 text-center">
            Showing {currentImages.length} of {filteredCount} images
            {selectedCategory !== 'All' && ` in "${selectedCategory}" category`}
            {totalPages > 1 && ` (Page ${currentPage} of ${totalPages})`}
          </p>
        </div>
      </div>

      {/* Image Grid */}
      <div className="bg-slate-900 px-6 py-8">
        <div className="max-w-6xl mx-auto">
          {currentImages.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {currentImages.map((image, index) => (
                <div
                  key={image.id || index}
                  className="group bg-slate-700 rounded-lg overflow-hidden shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105"
                >
                  <div className="aspect-[3/2] relative overflow-hidden">
                    <img
                      src={image.url}
                      alt={cleanTitle(image.title)}
                      className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                      onError={(e) => {
                        e.target.src = '/placeholder-image.jpg';
                      }}
                    />
                  </div>
                  
                  <div className="p-4">
                    <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-orange-400 transition-colors">
                      {cleanTitle(image.title)}
                    </h3>
                    {image.categories && image.categories.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {image.categories.map((category, idx) => (
                          <span key={idx} className="bg-orange-500 text-white text-xs px-2 py-1 rounded-full">
                            {category}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-slate-400 text-lg">
                {selectedCategory === 'All' 
                  ? 'No images available in the portfolio'
                  : `No images found in the "${selectedCategory}" category`
                }
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="bg-slate-900 px-6 py-8">
          <div className="max-w-6xl mx-auto">
            <div className="flex justify-center items-center gap-4">
              <button
                onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                disabled={currentPage === 1}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  currentPage === 1
                    ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                    : 'bg-slate-700 text-white hover:bg-slate-600'
                }`}
              >
                Previous
              </button>
              
              <div className="flex gap-2">
                {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => {
                  const url = new URL(window.location.origin + '/portfolio');
                  
                  // Debug logging
                  console.log('Generating URL for page', page, 'with category:', selectedCategory);
                  
                  if (selectedCategory && selectedCategory !== 'All') {
                    url.searchParams.set('category', selectedCategory);
                    console.log('Added category to URL:', selectedCategory);
                  }
                  if (page > 1) {
                    url.searchParams.set('page', page);
                    console.log('Added page to URL:', page);
                  }
                  
                  const finalUrl = url.pathname + url.search;
                  console.log('Final URL:', finalUrl);
                  
                  return (
                    <a
                      key={page}
                      href={finalUrl}
                      onClick={(e) => {
                        e.preventDefault();
                        setCurrentPage(page);
                      }}
                      className={`w-10 h-10 rounded-lg font-medium transition-all flex items-center justify-center ${
                        currentPage === page
                          ? 'bg-orange-500 text-white'
                          : 'bg-slate-700 text-slate-300 hover:bg-slate-600 hover:text-white'
                      }`}
                    >
                      {page}
                    </a>
                  );
                })}</div>
              
              <button
                onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                disabled={currentPage === totalPages}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  currentPage === totalPages
                    ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                    : 'bg-slate-700 text-white hover:bg-slate-600'
                }`}
              >
                Next
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SQLPortfolio;


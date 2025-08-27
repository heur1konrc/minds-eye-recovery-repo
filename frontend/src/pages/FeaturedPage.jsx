import React, { useState, useEffect } from 'react';

const FeaturedPage = () => {
  const [featuredImage, setFeaturedImage] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showFullscreen, setShowFullscreen] = useState(false);

  useEffect(() => {
    fetch('/api/featured-image')
      .then(response => response.json())
      .then(data => {
        console.log('Featured API Response:', data);
        if (data && !data.error && data.filename) {
          setFeaturedImage(data);
        }
        setLoading(false);
      })
      .catch(error => {
        console.error('Error:', error);
        setLoading(false);
      });
  }, []);

  // Handle escape key to close fullscreen
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        setShowFullscreen(false);
      }
    };

    if (showFullscreen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [showFullscreen]);

  const openFullscreen = () => {
    setShowFullscreen(true);
  };

  const closeFullscreen = () => {
    setShowFullscreen(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 pt-20">
        <div className="text-center py-12">
          <h1 className="text-4xl md:text-5xl font-bold text-orange-500 mb-4">
            WEEKLY FEATURED IMAGE
          </h1>
          <p className="text-slate-300">Loading...</p>
        </div>
      </div>
    );
  }

  if (!featuredImage) {
    return (
      <div className="min-h-screen bg-slate-900 pt-20">
        <div className="text-center py-12">
          <h1 className="text-4xl md:text-5xl font-bold text-orange-500 mb-4">
            WEEKLY FEATURED IMAGE
          </h1>
          <p className="text-slate-300">No featured image has been set yet.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 pt-20">
      <div className="text-center py-12">
        <h1 className="text-4xl md:text-5xl font-bold text-orange-500 mb-4">
          WEEKLY FEATURED IMAGE
        </h1>
      </div>

      <div className="max-w-6xl mx-auto px-6 pb-12">
        {/* A. LARGE FEATURED IMAGE */}
        <div className="mb-8">
          <div className="rounded-lg overflow-hidden shadow-2xl">
            <img
              src={`/data/${featuredImage.filename}`}
              alt={featuredImage.title || 'Featured Image'}
              className="w-full h-auto"
            />
          </div>
        </div>

        {/* BUTTONS AND EXIF DATA ROW */}
        <div className="grid md:grid-cols-2 gap-8 mb-8">
          {/* BUTTONS */}
          <div className="space-y-4">
            <button 
              onClick={openFullscreen}
              className="w-full bg-orange-500 hover:bg-orange-600 text-white font-bold py-3 px-6 rounded-lg transition-colors"
            >
              View Fullscreen
            </button>
            <a 
              href={`/data/${featuredImage.filename}`}
              download
              className="block w-full bg-green-500 hover:bg-green-600 text-white font-bold py-3 px-6 rounded-lg text-center transition-colors"
            >
              📥 Download Image
            </a>
          </div>

          {/* B. EXIF DATA */}
          <div className="bg-slate-800 rounded-lg p-6">
            <h3 className="text-xl font-bold text-orange-500 mb-4">Image Capture Information</h3>
            {featuredImage.exif_data && Object.keys(featuredImage.exif_data).length > 0 ? (
              <div className="space-y-2 text-slate-300">
                {Object.entries(featuredImage.exif_data).map(([key, value]) => (
                  <div key={key} className="flex justify-between">
                    <span className="capitalize">{key.replace('_', ' ')}:</span>
                    <span>{value}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-slate-400 italic">EXIF data not available for this image</p>
            )}
          </div>
        </div>

        {/* C. STORY SECTION - FULL WIDTH BELOW EVERYTHING */}
        {featuredImage.story && (
          <div className="bg-slate-800 rounded-lg p-6">
            <h3 className="text-xl font-bold text-orange-500 mb-4">Story Behind the Shot</h3>
            <p className="text-slate-300 leading-relaxed">{featuredImage.story}</p>
          </div>
        )}
      </div>

      {/* A. FULLSCREEN MODAL - CLEAN, ONLY X TO CLOSE */}
      {showFullscreen && (
        <div 
          className="fixed inset-0 bg-black z-50 flex items-center justify-center"
          onClick={closeFullscreen}
        >
          {/* ONLY WHITE X TO CLOSE */}
          <button
            onClick={closeFullscreen}
            className="absolute top-4 right-4 text-white text-4xl font-bold z-60 hover:text-orange-500 transition-colors"
            aria-label="Close fullscreen"
          >
            ×
          </button>
          
          {/* CLEAN IMAGE - NO TEXT */}
          <img
            src={`/data/${featuredImage.filename}`}
            alt={featuredImage.title || 'Featured Image'}
            className="max-w-full max-h-full object-contain"
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      )}
    </div>
  );
};

export default FeaturedPage;


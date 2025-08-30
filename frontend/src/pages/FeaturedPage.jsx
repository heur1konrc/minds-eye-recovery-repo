import React, { useState, useEffect } from 'react';

const FeaturedPage = () => {
  const [featuredImage, setFeaturedImage] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showFullscreen, setShowFullscreen] = useState(false);

  // Format capture date to MM/DD/YYYY
  const formatCaptureDate = (dateString) => {
    if (!dateString) return 'N/A';
    
    // Handle EXIF date format: "2025:08:09 01:57:47" or "2025:08:09"
    const datePart = dateString.split(' ')[0]; // Remove time part
    const [year, month, day] = datePart.split(':');
    
    if (year && month && day) {
      return `${month}/${day}/${year}`;
    }
    
    return dateString; // Return original if parsing fails
  };

  // Social sharing function
  const shareOnSocial = () => {
    const url = window.location.href;
    const text = `Check out this amazing featured image from Mind's Eye Photography!`;
    
    // Try native sharing first (mobile)
    if (navigator.share) {
      navigator.share({
        title: 'Mind\'s Eye Photography - Featured Image',
        text: text,
        url: url
      });
    } else {
      // Fallback to Twitter sharing
      const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`;
      window.open(twitterUrl, '_blank');
    }
  };

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
        {/* IMAGE AND RIGHT SIDEBAR LAYOUT */}
        <div className="grid lg:grid-cols-3 gap-8 mb-8">
          {/* A. LARGE FEATURED IMAGE - LEFT SIDE (2/3 width) */}
          <div className="lg:col-span-2">
            <div className="rounded-lg overflow-hidden shadow-2xl">
              <img
                src={`/data/${featuredImage.filename}`}
                alt={featuredImage.title || 'Featured Image'}
                className="w-full h-auto"
              />
            </div>
          </div>

          {/* RIGHT SIDEBAR - EXIF AND BUTTONS STACKED (1/3 width) */}
          <div className="space-y-6">
            {/* B. EXIF DATA - TOP */}
            <div className="bg-slate-800 rounded-lg p-6">
              <h3 className="text-xl font-bold text-orange-500 mb-4">Image Capture Information</h3>
              {featuredImage.exif_data && Object.keys(featuredImage.exif_data).length > 0 ? (
                <div className="space-y-2 text-slate-300">
                  {/* Combined Camera Make and Model */}
                  {featuredImage.exif_data.camera_model && (
                    <div className="flex justify-between">
                      <span>Camera Make and Model:</span>
                      <span>{featuredImage.exif_data.camera_model}</span>
                    </div>
                  )}
                  
                  {/* Other EXIF data (excluding camera_make and camera_model) */}
                  {Object.entries(featuredImage.exif_data)
                    .filter(([key]) => key !== 'camera_make' && key !== 'camera_model')
                    .map(([key, value]) => (
                      <div key={key} className="flex justify-between">
                        <span className="capitalize">{key.replace('_', ' ')}:</span>
                        <span>
                          {key === 'capture_date' ? formatCaptureDate(value) : value}
                        </span>
                      </div>
                    ))}
                </div>
              ) : (
                <p className="text-slate-400 italic">EXIF data not available for this image</p>
              )}
            </div>

            {/* BUTTONS - MIDDLE AND BOTTOM */}
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
            <button 
              onClick={shareOnSocial}
              className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 px-6 rounded-lg transition-colors"
            >
              🔗 Share on Social Media
            </button>
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

      {/* FIT-TO-SCREEN MODAL - LIKE PORTFOLIO */}
      {showFullscreen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center p-4"
          onClick={closeFullscreen}
        >
          {/* CLOSE BUTTON */}
          <button
            onClick={closeFullscreen}
            className="absolute top-4 right-4 text-white text-4xl font-bold z-60 hover:text-orange-500 transition-colors bg-black bg-opacity-50 rounded-full w-12 h-12 flex items-center justify-center"
            aria-label="Close modal"
          >
            ×
          </button>
          
          {/* FIT-TO-SCREEN IMAGE WITH TITLE */}
          <div className="max-w-6xl max-h-[90vh] flex flex-col items-center">
            <img
              src={`/data/${featuredImage.filename}`}
              alt={featuredImage.title || 'Featured Image'}
              className="max-w-full max-h-[80vh] object-contain rounded-lg shadow-2xl"
              onClick={(e) => e.stopPropagation()}
            />
            {/* IMAGE TITLE BELOW */}
            {featuredImage.title && (
              <div className="mt-4 text-center">
                <h3 className="text-2xl font-bold text-orange-500">{featuredImage.title}</h3>
                {featuredImage.description && (
                  <p className="text-slate-300 mt-2">{featuredImage.description}</p>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default FeaturedPage;


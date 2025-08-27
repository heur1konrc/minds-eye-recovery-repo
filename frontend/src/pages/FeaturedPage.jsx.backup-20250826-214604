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
          
          // Set Open Graph meta tags
          const setMetaTag = (property, content) => {
            let meta = document.querySelector(`meta[property="${property}"]`) || 
                      document.querySelector(`meta[name="${property}"]`);
            if (!meta) {
              meta = document.createElement('meta');
              if (property.startsWith('og:') || property.startsWith('twitter:')) {
                meta.setAttribute('property', property);
              } else {
                meta.setAttribute('name', property);
              }
              document.head.appendChild(meta);
            }
            meta.setAttribute('content', content);
          };
          
          // Set page title
          document.title = `${data.title} - Featured Image - Mind's Eye Photography`;
          
          // Set meta tags
          setMetaTag('description', data.story || `Featured photograph: ${data.title}`);
          setMetaTag('og:type', 'article');
          setMetaTag('og:url', window.location.href);
          setMetaTag('og:title', `${data.title} - Mind's Eye Photography`);
          setMetaTag('og:description', data.story || `Featured photograph: ${data.title}`);
          setMetaTag('og:image', `${window.location.origin}/data/${data.filename}`);
          setMetaTag('og:image:width', data.width || '1200');
          setMetaTag('og:image:height', data.height || '630');
          setMetaTag('og:site_name', "Mind's Eye Photography");
          setMetaTag('twitter:card', 'summary_large_image');
          setMetaTag('twitter:url', window.location.href);
          setMetaTag('twitter:title', `${data.title} - Mind's Eye Photography`);
          setMetaTag('twitter:description', data.story || `Featured photograph: ${data.title}`);
          setMetaTag('twitter:image', `${window.location.origin}/data/${data.filename}`);
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
      document.body.style.overflow = 'hidden'; // Prevent background scrolling
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

  if (!featuredImage) {
    return (
      <div className="min-h-screen bg-slate-900 pt-20">
        <div className="text-center py-12">
          <h1 className="text-4xl md:text-5xl font-bold text-orange-500 mb-4">
            WEEKLY FEATURED IMAGE
          </h1>
        </div>
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="text-2xl font-bold text-orange-500 mb-4">No Featured Image</h2>
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

      <div className="max-w-7xl mx-auto px-6 pb-12">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Featured Image - Using About page pattern */}
          <div className="lg:col-span-2">
            <div className="relative">
              <div className="rounded-lg overflow-hidden shadow-2xl">
                <img
                  src={`/data/${featuredImage.filename}`}
                  alt={featuredImage.title || 'Featured Image'}
                  className="w-full h-auto"
                  onError={(e) => {
                    console.error('Image failed to load:', `/data/${featuredImage.filename}`);
                    e.target.style.display = 'none';
                  }}
                  onLoad={() => {
                    console.log('Image loaded successfully:', `/data/${featuredImage.filename}`);
                  }}
                />
              </div>
            </div>
            
            {/* Story section moved here - under the image, same width */}
            {featuredImage.story && (
              <div className="bg-slate-800 rounded-lg p-6 mt-6">
                <h3 className="text-lg font-bold text-orange-500 mb-3">Story Behind the Shot</h3>
                <p className="text-slate-300 leading-relaxed">{featuredImage.story}</p>
              </div>
            )}
          </div>

          {/* Image Info */}
          <div className="space-y-6">
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

            {/* Social Media Sharing */}
            <div className="bg-slate-800 rounded-lg p-6">
              <h3 className="text-lg font-bold text-orange-500 mb-4">Share This Image</h3>
              <div className="grid grid-cols-2 gap-3">
                <a
                  href={`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(window.location.href)}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition-colors"
                >
                  📘 Facebook
                </a>
                <a
                  href={`https://twitter.com/intent/tweet?url=${encodeURIComponent(window.location.href)}&text=${encodeURIComponent(`Check out this amazing photo: ${featuredImage.title}`)}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center bg-sky-500 hover:bg-sky-600 text-white font-bold py-2 px-4 rounded-lg transition-colors"
                >
                  🐦 Twitter
                </a>
                <a
                  href={`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(window.location.href)}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center bg-blue-700 hover:bg-blue-800 text-white font-bold py-2 px-4 rounded-lg transition-colors"
                >
                  💼 LinkedIn
                </a>
                <button
                  onClick={() => {
                    if (navigator.share) {
                      navigator.share({
                        title: `${featuredImage.title} - Mind's Eye Photography`,
                        text: featuredImage.story || `Check out this amazing photo: ${featuredImage.title}`,
                        url: window.location.href
                      });
                    } else {
                      navigator.clipboard.writeText(window.location.href);
                      alert('Link copied to clipboard!');
                    }
                  }}
                  className="flex items-center justify-center bg-gray-600 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded-lg transition-colors"
                >
                  🔗 Share
                </button>
              </div>
            </div>

            <div className="text-center">
              <span className="inline-block bg-orange-500 text-white px-4 py-2 rounded-full text-sm font-bold">
                Featured Image
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Fullscreen Modal */}
      {showFullscreen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-95 z-50 flex items-center justify-center p-4"
          onClick={closeFullscreen}
        >
          {/* Close button */}
          <button
            onClick={closeFullscreen}
            className="absolute top-4 right-4 text-white hover:text-orange-500 text-4xl font-bold z-60 transition-colors"
            aria-label="Close fullscreen"
          >
            ×
          </button>
          
          {/* Fullscreen image - clean, no text overlay */}
          <img
            src={`/data/${featuredImage.filename}`}
            alt={featuredImage.title || 'Featured Image'}
            className="max-w-full max-h-full object-contain cursor-pointer"
            onClick={(e) => e.stopPropagation()} // Prevent closing when clicking on image
          />
        </div>
      )}
    </div>
  );
};

export default FeaturedPage;


import React, { useState, useEffect } from 'react';

const AboutMindsEye = () => {
  const [aboutData, setAboutData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showFullscreen, setShowFullscreen] = useState(false);

  useEffect(() => {
    fetch('/api/about-minds-eye')
      .then(response => response.json())
      .then(data => {
        console.log('About Minds Eye API Response:', data);
        if (data && !data.error) {
          setAboutData(data);
        }
        setLoading(false);
      })
      .catch(error => {
        console.error('Error:', error);
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        setShowFullscreen(false);
      }
    };

    // Right-click protection for images
    const handleContextMenu = (e) => {
      if (e.target.tagName === 'IMG') {
        e.preventDefault();
        return false;
      }
    };

    const handleDragStart = (e) => {
      if (e.target.tagName === 'IMG') {
        e.preventDefault();
        return false;
      }
    };

    const handleSelectStart = (e) => {
      if (e.target.tagName === 'IMG') {
        e.preventDefault();
        return false;
      }
    };

    if (showFullscreen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    // Add image protection event listeners
    document.addEventListener('contextmenu', handleContextMenu);
    document.addEventListener('dragstart', handleDragStart);
    document.addEventListener('selectstart', handleSelectStart);

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.removeEventListener('contextmenu', handleContextMenu);
      document.removeEventListener('dragstart', handleDragStart);
      document.removeEventListener('selectstart', handleSelectStart);
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
            About Mind's Eye Photography
          </h1>
          <p className="text-slate-300">Loading...</p>
        </div>
      </div>
    );
  }

  if (!aboutData) {
    return (
      <div className="min-h-screen bg-slate-900 pt-20">
        <div className="text-center py-12">
          <h1 className="text-4xl md:text-5xl font-bold text-orange-500 mb-4">
            About Mind's Eye Photography
          </h1>
          <p className="text-slate-300">No about content has been set yet.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 pt-20">
      <div className="text-center py-12">
        <h1 className="text-4xl md:text-5xl font-bold text-orange-500 mb-4">
          About Mind's Eye Photography
        </h1>
        <p className="text-slate-300 text-lg">Where Moments Meet Imagination</p>
      </div>

      <div className="max-w-6xl mx-auto px-6 pb-12">
        <div className="bg-slate-800 rounded-lg p-8">
          {/* IMAGE FLOATED LEFT WITH TEXT WRAPPED */}
          {aboutData.image && (
            <div className="float-left mr-6 mb-4">
              <img 
                src={`/data/${aboutData.image}`} 
                alt="About Mind's Eye Photography"
                className="w-120 h-auto rounded-lg shadow-lg cursor-pointer select-none"
                onClick={openFullscreen}
                onContextMenu={(e) => e.preventDefault()}
                onDragStart={(e) => e.preventDefault()}
                style={{
                  userSelect: 'none',
                  WebkitUserSelect: 'none',
                  MozUserSelect: 'none',
                  msUserSelect: 'none',
                  userDrag: 'none',
                  WebkitUserDrag: 'none',
                  KhtmlUserDrag: 'none',
                  MozUserDrag: 'none',
                  OUserDrag: 'none'
                }}
              />
              <p className="text-slate-400 text-sm mt-2 text-center italic">
                Click to view full screen image
              </p>
            </div>
          )}
          
          {/* MAIN CONTENT */}
          <div className="text-slate-300 text-lg leading-relaxed">
            {aboutData.content && aboutData.content.main_content && (
              <div 
                className="prose prose-invert prose-lg max-w-none"
                dangerouslySetInnerHTML={{ 
                  __html: aboutData.content.main_content 
                }}
              />
            )}
            
            {/* SIGNATURE */}
            {aboutData.content && aboutData.content.signature && (
              <div className="text-right mt-8 text-orange-500 font-bold text-xl">
                {aboutData.content.signature}
              </div>
            )}
          </div>
          
          {/* CLEAR FLOAT */}
          <div className="clear-both"></div>
        </div>
      </div>

      {/* FIT-TO-SCREEN MODAL */}
      {showFullscreen && aboutData.image && (
        <div className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50 p-4">
          <div className="relative w-full h-full max-w-6xl max-h-4xl flex items-center justify-center">
            <button
              onClick={closeFullscreen}
              className="absolute top-4 right-4 text-white text-4xl hover:text-gray-300 z-10 bg-black bg-opacity-50 rounded-full w-12 h-12 flex items-center justify-center"
            >
              ×
            </button>
            <img
              src={`/data/${aboutData.image}`}
              alt="About Mind's Eye Photography - Fit to Screen"
              className="max-w-full max-h-full object-contain rounded-lg shadow-2xl select-none"
              onContextMenu={(e) => e.preventDefault()}
              onDragStart={(e) => e.preventDefault()}
              style={{
                userSelect: 'none',
                WebkitUserSelect: 'none',
                MozUserSelect: 'none',
                msUserSelect: 'none',
                userDrag: 'none',
                WebkitUserDrag: 'none',
                KhtmlUserDrag: 'none',
                MozUserDrag: 'none',
                OUserDrag: 'none'
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default AboutMindsEye;


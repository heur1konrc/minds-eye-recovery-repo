import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import Logo from '../components/Logo'

const HomePage = () => {
  const [slideshowImages, setSlideshowImages] = useState([]);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [slideshowSettings, setSlideshowSettings] = useState({
    transition_duration: 5000,
    fade_duration: 1000,
    auto_play: true,
    pause_on_hover: true
  });
  const [loading, setLoading] = useState(true);
  const [isPaused, setIsPaused] = useState(false);

  useEffect(() => {
    const fetchSlideshowData = async () => {
      try {
        // Create logo slide as permanent first slide
        const logoSlide = {
          id: 'logo-slide',
          filename: 'logo-slide.png',
          title: "Mind's Eye Photography",
          url: '/logo-slide.png'
        };

        // Fetch slideshow images from slideshow-specific API (only toggled images)
        const slideshowResponse = await fetch('/api/slideshow');
        const slideshowData = await slideshowResponse.json();
        
        console.log('Slideshow API images:', slideshowData);
        
        if (slideshowData && slideshowData.length > 0) {
          // Use images marked for slideshow (respects toggle settings)
          const adminSlides = slideshowData.map(image => ({
            id: image.id,
            filename: image.filename,
            title: image.title,
            url: `/data/${image.filename}`  // Use /data path for persistent storage
          }));
          
          // Combine logo slide + slideshow-marked images
          const allSlides = [logoSlide, ...adminSlides];
          setSlideshowImages(allSlides);
          console.log('✅ Slideshow with marked images loaded:', allSlides.length, 'slides');
        } else {
          // Just logo slide if no slideshow images marked
          setSlideshowImages([logoSlide]);
          console.log('📝 Using logo slide only - no images marked for slideshow');
        }
        
        setLoading(false);
      } catch (error) {
        console.error('❌ Error fetching slideshow data:', error);
        // Fallback to just logo slide on error
        setSlideshowImages([{
          id: 'logo-slide',
          filename: 'logo-slide.png',
          title: "Mind's Eye Photography",
          url: '/logo-slide.png'
        }]);
        setLoading(false);
      }
    };

    fetchSlideshowData();
  }, []);

  // Slideshow auto-advance effect
  useEffect(() => {
    if (!slideshowSettings.auto_play || isPaused || slideshowImages.length <= 1) {
      return;
    }

    const interval = setInterval(() => {
      setCurrentImageIndex((prevIndex) => 
        (prevIndex + 1) % slideshowImages.length
      );
    }, slideshowSettings.transition_duration);

    return () => clearInterval(interval);
  }, [slideshowImages.length, slideshowSettings.transition_duration, slideshowSettings.auto_play, isPaused]);

  const handleMouseEnter = () => {
    if (slideshowSettings.pause_on_hover) {
      setIsPaused(true);
    }
  };

  const handleMouseLeave = () => {
    if (slideshowSettings.pause_on_hover) {
      setIsPaused(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading slideshow...</div>
      </div>
    );
  }

  return (
    <div 
      className="min-h-screen relative overflow-hidden pt-20"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {/* Slideshow Background Images - SIMPLE IMG APPROACH */}
      <div className="absolute inset-0">
        {slideshowImages.map((image, index) => (
          <img
            key={image.id || index}
            src={image.url}
            alt={image.title || 'Slideshow Image'}
            className="absolute inset-0 w-full h-full object-cover transition-opacity duration-1000"
            style={{
              opacity: index === currentImageIndex ? 1 : 0,
              zIndex: index === currentImageIndex ? 5 : 1
            }}
            onLoad={() => console.log(`✅ Image ${index + 1} loaded:`, image.url)}
            onError={(e) => console.error(`❌ Image ${index + 1} failed:`, image.url, e)}
          />
        ))}
        
        {/* Subtle overlay for text readability - Behind images */}
        <div className="absolute inset-0 bg-black bg-opacity-20" style={{zIndex: -1}}></div>
      </div>

      {/* Corner Logo and Tagline - TEMPORARILY REMOVED FOR TESTING */}
      {/*
      <div className="absolute top-6 left-6 z-10">
        <motion.div
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 1, delay: 0.5 }}
          className="bg-black bg-opacity-40 backdrop-blur-sm rounded-lg p-4"
        >
          <div className="flex flex-col items-start">
            <Logo className="h-20 w-auto mb-2" />
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 1, delay: 1 }}
              className="text-white text-sm font-light tracking-wide"
            >
              Where Moments Meet Imagination
            </motion.p>
          </div>
        </motion.div>
      </div>
      */}

      {/* Navigation Menu - Top Right - REMOVED FOR CLEAN DESIGN */}

      {/* Center Content - Minimal and Elegant */}
      {/* View Portfolio Button - Bottom Right Corner */}
      <div className="absolute bottom-6 right-6 z-10">
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 1.5 }}
          className="flex flex-col items-center justify-center text-center"
        >
          <Link
            to="/portfolio"
            className="inline-block bg-orange-500 hover:bg-orange-600 text-white font-semibold py-4 px-8 rounded-lg transition-all duration-300 transform hover:scale-105 shadow-lg"
          >
            View Portfolio
          </Link>
        </motion.div>
      </div>

      {/* Slideshow Indicators - Bottom Center */}
      {slideshowImages.length > 1 && (
        <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 z-10">
          <div className="flex space-x-2">
            {slideshowImages.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentImageIndex(index)}
                className={`w-3 h-3 rounded-full transition-all duration-300 ${
                  index === currentImageIndex 
                    ? 'bg-orange-500 scale-125' 
                    : 'bg-white bg-opacity-50 hover:bg-opacity-75'
                }`}
              />
            ))}
          </div>
        </div>
      )}

      {/* Slideshow Info - Bottom Left - REMOVED FOR CLEAN DESIGN */}
    </div>
  );
};

export default HomePage;


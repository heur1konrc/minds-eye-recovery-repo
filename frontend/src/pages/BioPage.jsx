import React, { useState, useEffect } from 'react';

const BioPage = () => {
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dataLoaded, setDataLoaded] = useState(false);

  useEffect(() => {
    fetch('/api/about-images')
      .then(response => response.json())
      .then(data => {
        console.log('About images loaded:', data);
        setImages(data || []);
        setDataLoaded(true);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error loading images:', error);
        setDataLoaded(true); // Mark as loaded even on error
        setLoading(false);
      });
  }, []);

  // Show loading until we have confirmed data load (success or failure)
  if (loading || !dataLoaded) {
    return <div className="min-h-screen bg-slate-900 flex items-center justify-center text-white">Loading...</div>;
  }

  const firstImage = images[0];
  const galleryImages = images.slice(1);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800">
      <div className="container mx-auto px-6 py-16">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-5xl md:text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-red-500 mb-4">
            About Mind's Eye Photography
          </h1>
          <p className="text-xl text-blue-200 font-light">
            Where Moments Meet Imagination
          </p>
        </div>

        {/* Bio Content */}
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col lg:flex-row gap-8 items-start">
            {/* First Image - Inline */}
            <div className="lg:w-1/3 mb-8 lg:mb-0">
              {firstImage ? (
                <div className="relative group">
                  <img
                    src={`/data/${firstImage.filename}`}
                    alt={firstImage.title}
                    className="w-full h-auto rounded-lg shadow-2xl"
                  />
                </div>
              ) : (
                <div className="w-full h-96 bg-gray-600 rounded-lg flex items-center justify-center text-white text-center p-8">
                  <div>
                    <h3 className="text-xl font-bold mb-2">Behind the Lens Image</h3>
                    <p>Upload image in admin</p>
                  </div>
                </div>
              )}
              <p className="text-center text-orange-400 mt-4 font-medium">
                {firstImage ? firstImage.title : 'Behind the Lens'}
              </p>
            </div>

            {/* Bio Text */}
            <div className="lg:w-2/3">
              <div className="prose prose-lg prose-invert max-w-none">
                <p className="text-lg leading-relaxed text-gray-300 mb-6">
                  Born and raised right here in Madison, Wisconsin, I'm a creative spirit with a passion for bringing visions to life. My journey has woven through various rewarding paths – as a <strong className="text-orange-400">musician/songwriter</strong>, a <strong className="text-orange-400">Teacher</strong>, a <strong className="text-orange-400">REALTOR</strong>, and a <strong className="text-orange-400">Small Business Owner</strong>. Each of these roles has fueled my inspired, creative, and driven approach to everything I do, especially when it comes to photography.
                </p>

                <p className="text-lg leading-relaxed text-gray-300 mb-6">
                  At the heart of Mind's Eye Photography: Where Moments Meet Imagination is my dedication to you. While I cherish the fulfillment of capturing moments that spark my own imagination, my true passion lies in doing the same for my clients. Based in Madison, I frequently travel across the state, always on the lookout for that next inspiring scene.
                </p>

                <p className="text-lg leading-relaxed text-gray-300 mb-8">
                  For me, client satisfaction isn't just a goal – it's the foundation of every interaction. I pour my energy into ensuring you not only love your photos but also enjoy the entire experience. It's truly rewarding to see clients transform into lifelong friends, and that's the kind of connection I strive to build with everyone I work with.
                </p>

                <p className="text-xl font-semibold text-orange-400">
                  Rick Corey
                </p>
              </div>
            </div>
          </div>

          {/* Gallery Images at Bottom */}
          {galleryImages.length > 0 && (
            <div className="mt-16">
              <h2 className="text-3xl font-bold text-orange-400 text-center mb-8">
                More Behind the Scenes
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {galleryImages.map((image) => (
                  <div key={image.id} className="relative group">
                    <img
                      src={`/data/${image.filename}`}
                      alt={image.title}
                      className="w-full h-64 object-cover rounded-lg shadow-2xl"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end">
                      <div className="p-4">
                        <h3 className="text-white font-semibold text-lg">{image.title}</h3>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default BioPage;


import React, { useState, useEffect } from 'react';

const AboutYou = () => {
  const [aboutImage, setAboutImage] = useState(null);
  const [aboutContent, setAboutContent] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch the selected about image
    fetch('/api/about-image')
      .then(response => response.json())
      .then(data => {
        if (data.success && data.image) {
          setAboutImage(data.image);
        }
      })
      .catch(error => {
        console.error('Error loading about image:', error);
      });

    // Fetch about content from admin
    fetch('/api/about-content')
      .then(response => response.json())
      .then(data => {
        if (data.success && data.content) {
          setAboutContent(data.content);
        } else {
          // Default content if none set in admin
          setAboutContent(`Born and raised right here in Madison, Wisconsin, I'm a creative spirit with a passion for bringing visions to life. My journey has woven through various rewarding paths – as a musician/songwriter, a Teacher, a REALTOR, and a Small Business Owner. Each of these roles has fueled my inspired, creative, and driven approach to everything I do, especially when it comes to photography.

At the heart of Mind's Eye Photography: Where Moments Meet Imagination is my dedication to you. While I cherish the fulfillment of capturing moments that spark my own imagination, my true passion lies in doing the same for my clients. Based in Madison, I frequently travel across the state, always on the lookout for that next inspiring scene.

For me, client satisfaction isn't just a goal – it's the foundation of every interaction. I pour my energy into ensuring you not only love your photos but also enjoy the entire experience. It's truly rewarding to see clients transform into lifelong friends, and that's the kind of connection I strive to build with everyone I work with.`);
        }
        setLoading(false);
      })
      .catch(error => {
        console.error('Error loading about content:', error);
        // Use default content on error
        setAboutContent(`Born and raised right here in Madison, Wisconsin, I'm a creative spirit with a passion for bringing visions to life. My journey has woven through various rewarding paths – as a musician/songwriter, a Teacher, a REALTOR, and a Small Business Owner. Each of these roles has fueled my inspired, creative, and driven approach to everything I do, especially when it comes to photography.

At the heart of Mind's Eye Photography: Where Moments Meet Imagination is my dedication to you. While I cherish the fulfillment of capturing moments that spark my own imagination, my true passion lies in doing the same for my clients. Based in Madison, I frequently travel across the state, always on the lookout for that next inspiring scene.

For me, client satisfaction isn't just a goal – it's the foundation of every interaction. I pour my energy into ensuring you not only love your photos but also enjoy the entire experience. It's truly rewarding to see clients transform into lifelong friends, and that's the kind of connection I strive to build with everyone I work with.`);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-orange-500 text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Header */}
      <div className="bg-slate-900 py-20">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <h1 className="text-4xl md:text-5xl font-light text-orange-500 mb-6">
            About Mind's Eye Photography
          </h1>
          <p className="text-xl text-slate-300">
            Where Moments Meet Imagination
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-16">
        <div className="flex flex-col lg:flex-row gap-12 items-start">
          
          {/* Left Side - About Image */}
          <div className="lg:w-1/2">
            {aboutImage ? (
              <div className="relative">
                <img
                  src={`/data/${aboutImage.filename}`}
                  alt={aboutImage.title}
                  className="w-full h-auto rounded-lg shadow-2xl"
                />
                <div className="mt-4">
                  <h3 className="text-xl font-medium text-orange-400 text-center">
                    {aboutImage.title}
                  </h3>
                </div>
              </div>
            ) : (
              <div className="w-full h-96 bg-slate-800 rounded-lg flex items-center justify-center">
                <div className="text-center text-slate-400">
                  <p>No About image selected</p>
                  <p className="text-sm mt-2">Use admin dashboard to set an About image</p>
                </div>
              </div>
            )}
          </div>

          {/* Right Side - About Content */}
          <div className="lg:w-1/2">
            <div className="prose prose-lg prose-invert max-w-none">
              <div className="text-slate-300 leading-relaxed text-lg space-y-6">
                {aboutContent.split('\n\n').map((paragraph, index) => (
                  <p key={index} className="mb-6">
                    {paragraph.split('\n').map((line, lineIndex) => (
                      <span key={lineIndex}>
                        {line.split(/(\*\*.*?\*\*)/).map((part, partIndex) => {
                          if (part.startsWith('**') && part.endsWith('**')) {
                            return (
                              <strong key={partIndex} className="text-orange-400">
                                {part.slice(2, -2)}
                              </strong>
                            );
                          }
                          return part;
                        })}
                        {lineIndex < paragraph.split('\n').length - 1 && <br />}
                      </span>
                    ))}
                  </p>
                ))}
              </div>
              
              <div className="mt-8 text-right">
                <p className="text-xl font-semibold text-orange-400">
                  Rick Corey
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AboutYou;


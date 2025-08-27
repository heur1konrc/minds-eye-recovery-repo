import React, { useState, useEffect } from 'react';

const AboutYou = () => {
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/simple-portfolio')
      .then(response => response.json())
      .then(data => {
        console.log('API Response:', data);
        const batchImage = data.find(img => img.title === 'Batch upload 1');
        console.log('Found Batch upload 1:', batchImage);
        setImage(batchImage);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error:', error);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div className="min-h-screen bg-black flex items-center justify-center text-white">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      {image ? (
        <img 
          src={`/data/${image.filename}`} 
          alt={image.title}
          className="max-w-full max-h-full object-contain"
        />
      ) : (
        <div className="text-white text-xl">Image "Batch upload 1" not found</div>
      )}
    </div>
  );
};

export default AboutYou;


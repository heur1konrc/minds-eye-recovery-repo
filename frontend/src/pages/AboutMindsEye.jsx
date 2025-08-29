import React from 'react';

const AboutMindsEye = () => {
  console.log('AboutMindsEye component is rendering!');
  
  return (
    <div className="min-h-screen bg-slate-900 pt-20">
      <div className="text-center py-12">
        <h1 className="text-4xl md:text-5xl font-bold text-orange-500 mb-4">
          TEST: About Mind's Eye Photography
        </h1>
        <p className="text-slate-300 text-lg">This is a test to see if the component renders</p>
      </div>
    </div>
  );
};

export default AboutMindsEye;


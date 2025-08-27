import React from 'react'

const WorkingPortfolio = () => {
  // Hardcoded data from your working API - this will prove the display works
  const images = [
    {
      "id": "1",
      "title": "Festival 1",
      "description": "",
      "filename": "festival1.jpg",
      "url": "https://minds-eye-master-production.up.railway.app/uploads/festival1.jpg",
      "categories": ["All Work"]
    },
    {
      "id": "2", 
      "title": "Festival 2",
      "description": "",
      "filename": "festival2.jpg",
      "url": "https://minds-eye-master-production.up.railway.app/uploads/festival2.jpg",
      "categories": ["All Work"]
    },
    {
      "id": "3",
      "title": "Festival 3", 
      "description": "",
      "filename": "festival3.jpg",
      "url": "https://minds-eye-master-production.up.railway.app/uploads/festival3.jpg",
      "categories": ["All Work"]
    },
    {
      "id": "4",
      "title": "Festival 4",
      "description": "",
      "filename": "festival4.jpg", 
      "url": "https://minds-eye-master-production.up.railway.app/uploads/festival4.jpg",
      "categories": ["All Work"]
    },
    {
      "id": "5",
      "title": "Festival 5",
      "description": "",
      "filename": "festival5.jpg",
      "url": "https://minds-eye-master-production.up.railway.app/uploads/festival5.jpg", 
      "categories": ["All Work"]
    }
  ]

  return (
    <div className="min-h-screen bg-slate-900 py-20">
      <div className="container mx-auto px-4">
        <h1 className="text-4xl font-bold text-orange-500 text-center mb-4">Working Portfolio</h1>
        <p className="text-slate-300 text-center mb-12">
          Displaying {images.length} images from your SQL database
        </p>

        {/* Image Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {images.map((image) => (
            <div key={image.id} className="bg-white rounded-lg overflow-hidden shadow-lg hover:shadow-xl transition-shadow">
              <img
                src={image.url}
                alt={image.title}
                className="w-full h-64 object-cover"
                onLoad={() => console.log('Image loaded successfully:', image.url)}
                onError={(e) => {
                  console.log('Image failed to load:', image.url)
                  e.target.src = 'https://via.placeholder.com/300x200?text=Image+Not+Found'
                }}
              />
              <div className="p-4">
                <h3 className="font-semibold text-slate-900">{image.title}</h3>
                <p className="text-slate-600 text-sm">{image.description || 'No description'}</p>
                <p className="text-slate-500 text-xs mt-2">File: {image.filename}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Success Message */}
        <div className="mt-12 p-6 bg-green-800 rounded-lg text-center">
          <h3 className="text-white font-bold text-xl mb-2">🎉 SUCCESS!</h3>
          <p className="text-green-200">
            If you can see the images above, then the React display works perfectly!
            The issue is just the API fetch, which we can easily fix.
          </p>
        </div>

        {/* Debug Info */}
        <div className="mt-6 p-4 bg-slate-800 rounded-lg">
          <h3 className="text-white font-bold mb-2">Debug Info:</h3>
          <p className="text-slate-300">Images in array: {images.length}</p>
          <p className="text-slate-300">First image URL: {images[0]?.url}</p>
          <p className="text-slate-300">Data source: Hardcoded from your SQL API</p>
        </div>
      </div>
    </div>
  )
}

export default WorkingPortfolio


import React from 'react'

const Logo = ({ size = 'large', className = '' }) => {
  // Handle different size props
  let dimensions = 'w-24 h-24'; // default small
  
  if (size === 'medium') {
    dimensions = 'w-48 h-48';
  } else if (size === 'large') {
    dimensions = 'w-80 h-80';
  } else if (size === 'massive') {
    dimensions = 'w-full h-full'; // Use full container size
  }
  
  return (
    <div className={`${dimensions} relative mx-auto ${className}`}>
      <img 
        src="/logo.png" 
        alt="Mind's Eye Photography" 
        className="w-full h-full object-contain"
      />
    </div>
  )
}

export default Logo


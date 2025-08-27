import React, { useEffect } from 'react'

const ImageProtection = ({ children, allowDownload = false }) => {
  useEffect(() => {
    // Disable right-click context menu globally
    const handleContextMenu = (e) => {
      // If this is the featured image and download is allowed, let it through
      if (allowDownload && e.target.tagName === 'IMG') {
        return true
      }
      
      // For all other images, prevent context menu and show copyright message
      e.preventDefault()
      
      // Show copyright alert
      alert('Copyright Mind\'s Eye Photography 2025\nUse contact form for license options')
      
      return false
    }

    // Disable drag and drop for images
    const handleDragStart = (e) => {
      if (e.target.tagName === 'IMG' && !allowDownload) {
        e.preventDefault()
        return false
      }
    }

    // Disable text selection for images
    const handleSelectStart = (e) => {
      if (e.target.tagName === 'IMG' && !allowDownload) {
        e.preventDefault()
        return false
      }
    }

    // Add event listeners
    document.addEventListener('contextmenu', handleContextMenu)
    document.addEventListener('dragstart', handleDragStart)
    document.addEventListener('selectstart', handleSelectStart)

    // Cleanup
    return () => {
      document.removeEventListener('contextmenu', handleContextMenu)
      document.removeEventListener('dragstart', handleDragStart)
      document.removeEventListener('selectstart', handleSelectStart)
    }
  }, [allowDownload])

  return (
    <div 
      style={{
        userSelect: allowDownload ? 'auto' : 'none',
        WebkitUserSelect: allowDownload ? 'auto' : 'none',
        MozUserSelect: allowDownload ? 'auto' : 'none',
        msUserSelect: allowDownload ? 'auto' : 'none',
        WebkitTouchCallout: allowDownload ? 'default' : 'none',
        WebkitUserDrag: allowDownload ? 'auto' : 'none',
        KhtmlUserSelect: allowDownload ? 'auto' : 'none'
      }}
    >
      {children}
    </div>
  )
}

export default ImageProtection


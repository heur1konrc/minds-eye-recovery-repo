import { useEffect } from 'react';

const CopyrightProtection = () => {
  useEffect(() => {
    // Show copyright dialog on right-click instead of blocking
    const handleContextMenu = (e) => {
      // Only show dialog for images
      if (e.target.tagName === 'IMG') {
        // Check if this is the featured image in fullscreen modal (allow right-click)
        const isFullscreenModal = e.target.closest('.fixed.inset-0.bg-black.bg-opacity-95');
        if (isFullscreenModal) {
          // Allow right-click on featured image in fullscreen
          return true;
        }
        
        // Block right-click on all other images and show copyright message
        e.preventDefault();
        alert('Copyright Mind\'s Eye Photography 2025\nUse contact form for license options');
        return false;
      }
    };

    // Disable keyboard shortcuts only for image-related actions
    const handleKeyDown = (e) => {
      // Only block Ctrl+S (Save Page) to prevent saving images
      if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        alert('Copyright Mind\'s Eye Photography 2025\nUse contact form for license options');
        return false;
      }
      
      // Allow all other keyboard shortcuts for normal browsing
    };

    // Disable drag and drop on images (except featured image in fullscreen)
    const handleDragStart = (e) => {
      if (e.target.tagName === 'IMG') {
        // Check if this is the featured image in fullscreen modal
        const isFullscreenModal = e.target.closest('.fixed.inset-0.bg-black.bg-opacity-95');
        if (isFullscreenModal) {
          // Allow drag on featured image in fullscreen
          return true;
        }
        
        // Block drag on all other images
        e.preventDefault();
        return false;
      }
    };

    // Disable text selection on images (except featured image in fullscreen)
    const handleSelectStart = (e) => {
      if (e.target.tagName === 'IMG') {
        // Check if this is the featured image in fullscreen modal
        const isFullscreenModal = e.target.closest('.fixed.inset-0.bg-black.bg-opacity-95');
        if (isFullscreenModal) {
          // Allow selection on featured image in fullscreen
          return true;
        }
        
        // Block selection on all other images
        e.preventDefault();
        return false;
      }
    };

    // Add event listeners
    document.addEventListener('contextmenu', handleContextMenu);
    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('dragstart', handleDragStart);
    document.addEventListener('selectstart', handleSelectStart);

    // Add CSS to prevent image selection and dragging (except for fullscreen modal)
    const style = document.createElement('style');
    style.textContent = `
      img {
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        -ms-user-select: none !important;
        user-select: none !important;
        -webkit-user-drag: none !important;
        -khtml-user-drag: none !important;
        -moz-user-drag: none !important;
        -o-user-drag: none !important;
        user-drag: none !important;
        pointer-events: auto !important;
      }
      
      /* Allow selection and drag for featured image in fullscreen modal */
      .fixed.inset-0.bg-black.bg-opacity-95 img {
        -webkit-user-select: auto !important;
        -moz-user-select: auto !important;
        -ms-user-select: auto !important;
        user-select: auto !important;
        -webkit-user-drag: auto !important;
        -khtml-user-drag: auto !important;
        -moz-user-drag: auto !important;
        -o-user-drag: auto !important;
        user-drag: auto !important;
      }
      
      /* Disable long-press on mobile (except fullscreen) */
      img {
        -webkit-touch-callout: none !important;
        -webkit-tap-highlight-color: transparent !important;
      }
      
      .fixed.inset-0.bg-black.bg-opacity-95 img {
        -webkit-touch-callout: default !important;
      }
      
      /* Prevent image highlighting (except fullscreen) */
      img::selection {
        background: transparent !important;
      }
      
      img::-moz-selection {
        background: transparent !important;
      }
      
      .fixed.inset-0.bg-black.bg-opacity-95 img::selection {
        background: rgba(255, 255, 255, 0.3) !important;
      }
      
      .fixed.inset-0.bg-black.bg-opacity-95 img::-moz-selection {
        background: rgba(255, 255, 255, 0.3) !important;
      }
    `;
    document.head.appendChild(style);

    // Cleanup function
    return () => {
      document.removeEventListener('contextmenu', handleContextMenu);
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('dragstart', handleDragStart);
      document.removeEventListener('selectstart', handleSelectStart);
      if (style.parentNode) {
        style.parentNode.removeChild(style);
      }
    };
  }, []);

  return null; // This component doesn't render anything visible
};

export default CopyrightProtection;


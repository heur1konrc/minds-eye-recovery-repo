// FORCIBLY REMOVE ABOUT BUTTON AND ADD INFO BUTTON
function removeAboutAndAddInfo() {
  // Remove About button from desktop navigation
  const desktopLinks = document.querySelectorAll('nav a');
  desktopLinks.forEach(link => {
    if (link.textContent.trim() === 'About') {
      link.remove();
    }
  });
  
  // Remove About button from mobile navigation
  const mobileLinks = document.querySelectorAll('div a');
  mobileLinks.forEach(link => {
    if (link.textContent.trim() === 'About') {
      link.remove();
    }
  });
  
  // Add Info button to desktop navigation (after Featured)
  const desktopNav = document.querySelector('nav .hidden.md\\:flex');
  if (desktopNav && !document.querySelector('a[href="/info"]')) {
    const infoLink = document.createElement('a');
    infoLink.href = '/info';
    infoLink.textContent = 'Info';
    infoLink.className = 'text-white hover:text-orange-400 transition-colors';
    
    // Insert after Featured link
    const featuredLink = Array.from(desktopNav.children).find(link => 
      link.textContent.trim() === 'Featured'
    );
    if (featuredLink) {
      featuredLink.insertAdjacentElement('afterend', infoLink);
    }
  }
  
  // Add Info button to mobile navigation
  const mobileNav = document.querySelector('.flex-1.py-6');
  if (mobileNav && !document.querySelector('a[href="/info"]')) {
    const infoDiv = document.createElement('div');
    const infoLink = document.createElement('a');
    infoLink.href = '/info';
    infoLink.textContent = 'Info';
    infoLink.className = 'block px-6 py-4 text-lg transition-colors border-l-4 text-white border-transparent hover:text-orange-400 hover:border-orange-500/50 hover:bg-slate-800/30';
    infoDiv.appendChild(infoLink);
    
    // Insert after Featured in mobile menu
    const mobileLinks = mobileNav.children;
    if (mobileLinks.length >= 3) {
      mobileLinks[2].insertAdjacentElement('afterend', infoDiv);
    }
  }
  
  console.log('About button removed, Info button added (React route)');
}

// Run immediately and repeatedly
removeAboutAndAddInfo();
setInterval(removeAboutAndAddInfo, 100);


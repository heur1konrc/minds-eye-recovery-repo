// FORCIBLY REMOVE ABOUT BUTTON FROM SITE
function removeAboutButton() {
  // Remove from desktop navigation
  const desktopLinks = document.querySelectorAll('nav a');
  desktopLinks.forEach(link => {
    if (link.textContent.trim() === 'About') {
      link.remove();
    }
  });
  
  // Remove from mobile navigation
  const mobileLinks = document.querySelectorAll('div a');
  mobileLinks.forEach(link => {
    if (link.textContent.trim() === 'About') {
      link.remove();
    }
  });
  
  console.log('About button removed');
}

// Run immediately and repeatedly
removeAboutButton();
setInterval(removeAboutButton, 100);


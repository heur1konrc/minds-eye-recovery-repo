import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import Logo from './Logo'

const Navigation = () => {
  const location = useLocation()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  
  const navItems = [
    { path: '/', label: 'Home' },
    { path: '/portfolio', label: 'Portfolio' },
    { path: '/featured', label: 'Featured' },
    { path: '/about', label: 'About' },
    { path: '/contact', label: 'Contact' }
  ]

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen)
  }

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false)
  }

  return (
    <>
      <nav className="fixed top-0 left-0 right-0 z-50 bg-black/95 backdrop-blur-sm border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-6 pt-4 pb-2">
          <div className="flex justify-between items-center">
            {/* Logo/Brand with Small Logo */}
            <Link 
              to="/" 
              className="flex items-center space-x-3 text-orange-500 text-xl font-bold hover:text-orange-400 transition-colors"
              onClick={closeMobileMenu}
            >
              <div className="w-8 h-8">
                <Logo size="small" className="w-full h-full" />
              </div>
              <span>Mind's Eye Photography</span>
            </Link>
            
            {/* Desktop Navigation Links */}
            <div className="hidden md:flex space-x-8">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`relative transition-colors ${
                    location.pathname === item.path
                      ? 'text-orange-400'
                      : 'text-white hover:text-orange-400'
                  }`}
                >
                  {item.label}
                  {location.pathname === item.path && (
                    <motion.div
                      layoutId="activeTab"
                      className="absolute -bottom-1 left-0 right-0 h-0.5 bg-orange-500"
                      initial={false}
                      transition={{ type: "spring", stiffness: 500, damping: 30 }}
                    />
                  )}
                </Link>
              ))}
            </div>
            
            {/* Mobile Menu Button */}
            <div className="md:hidden">
              <button 
                onClick={toggleMobileMenu}
                className="text-white hover:text-orange-400 transition-colors p-2"
                aria-label="Toggle mobile menu"
              >
                <motion.div
                  animate={isMobileMenuOpen ? "open" : "closed"}
                  className="w-6 h-6 flex flex-col justify-center items-center"
                >
                  <motion.span
                    variants={{
                      closed: { rotate: 0, y: 0 },
                      open: { rotate: 45, y: 6 }
                    }}
                    className="w-6 h-0.5 bg-current block mb-1.5 origin-center"
                  />
                  <motion.span
                    variants={{
                      closed: { opacity: 1 },
                      open: { opacity: 0 }
                    }}
                    className="w-6 h-0.5 bg-current block mb-1.5"
                  />
                  <motion.span
                    variants={{
                      closed: { rotate: 0, y: 0 },
                      open: { rotate: -45, y: -6 }
                    }}
                    className="w-6 h-0.5 bg-current block origin-center"
                  />
                </motion.div>
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Mobile Menu Overlay */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 z-40 md:hidden"
              onClick={closeMobileMenu}
            />
            
            {/* Mobile Menu Panel */}
            <motion.div
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={{ type: "spring", stiffness: 300, damping: 30 }}
              className="fixed top-0 right-0 h-full w-80 bg-slate-900 z-50 md:hidden shadow-2xl"
            >
              <div className="flex flex-col h-full">
                {/* Mobile Menu Header */}
                <div className="flex justify-between items-center p-6 border-b border-slate-700">
                  <h2 className="text-orange-500 text-lg font-bold">Menu</h2>
                  <button
                    onClick={closeMobileMenu}
                    className="text-white hover:text-orange-400 transition-colors p-2"
                    aria-label="Close mobile menu"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                
                {/* Mobile Navigation Links */}
                <div className="flex-1 py-6">
                  {navItems.map((item, index) => (
                    <motion.div
                      key={item.path}
                      initial={{ opacity: 0, x: 50 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <Link
                        to={item.path}
                        onClick={closeMobileMenu}
                        className={`block px-6 py-4 text-lg transition-colors border-l-4 ${
                          location.pathname === item.path
                            ? 'text-orange-400 border-orange-500 bg-slate-800/50'
                            : 'text-white border-transparent hover:text-orange-400 hover:border-orange-500/50 hover:bg-slate-800/30'
                        }`}
                      >
                        {item.label}
                      </Link>
                    </motion.div>
                  ))}
                </div>
                
                {/* Mobile Menu Footer */}
                <div className="p-6 border-t border-slate-700">
                  <p className="text-slate-400 text-sm text-center">
                    © 2025 Mind's Eye Photography
                  </p>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  )
}

export default Navigation


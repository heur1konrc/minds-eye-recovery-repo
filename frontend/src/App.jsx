import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import Navigation from './components/Navigation'
import HomePage from './pages/HomePage'
import PortfolioPage from './pages/PortfolioPage'
import SimplePortfolio from './pages/SimplePortfolio'
import WorkingPortfolio from './pages/WorkingPortfolio'
import SQLPortfolio from './pages/SQLPortfolio'
import DirectPortfolio from './pages/DirectPortfolio'
import FeaturedPage from './pages/FeaturedPage'
import AboutMindsEye from './pages/AboutMindsEye'
import ContactPage from './pages/ContactPage'
import CopyrightProtection from './components/CopyrightProtection'
import './App.css'

// Portfolio redirect component - instant redirect
const PortfolioRedirect = () => {
  // Immediate redirect - no delay
  window.location.replace('/portfolio');
  return null; // Don't render anything
};

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <CopyrightProtection />
        <Navigation />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/portfolio" element={<SQLPortfolio />} />
          <Route path="/simple" element={<SimplePortfolio />} />
          <Route path="/working" element={<WorkingPortfolio />} />
          <Route path="/sql" element={<SQLPortfolio />} />
          <Route path="/featured" element={<FeaturedPage />} />
          <Route path="/info" element={<AboutMindsEye />} />
          <Route path="/contact" element={<ContactPage />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App

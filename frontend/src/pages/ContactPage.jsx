import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Mail, Phone, MapPin, Send } from 'lucide-react'
import { Button } from '@/components/ui/button'

const ContactPage = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    photography_type: '',
    message: ''
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitMessage, setSubmitMessage] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsSubmitting(true)
    setSubmitMessage('')
    
    try {
      const response = await fetch('/api/contact', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      })
      
      const result = await response.json()
      
      if (result.success) {
        setSubmitMessage('Thank you for your message! We will get back to you soon.')
        setFormData({ 
          name: '', 
          email: '', 
          phone: '', 
          photography_type: '', 
          message: '' 
        })
      } else {
        setSubmitMessage(result.error || 'An error occurred. Please try again.')
      }
    } catch (error) {
      setSubmitMessage('Network error. Please contact us directly at info@themindseyestudio.com')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Header */}
      <div className="bg-slate-900 py-20">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <motion.h1 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-4xl md:text-5xl font-light text-orange-500 mb-6"
          >
            Get In Touch
          </motion.h1>
          <motion.p 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-xl text-slate-300"
          >
            Ready to capture your perfect moment? Let's discuss your project.
          </motion.p>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 py-16">
        <div className="grid lg:grid-cols-2 gap-12">
          {/* Contact Information */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
          >
            <div className="bg-slate-800 rounded-lg p-8">
              <h2 className="text-2xl font-bold text-white mb-6">Contact Information</h2>
              
              <div className="space-y-6">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-orange-500 rounded-full flex items-center justify-center">
                    <Mail className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-white">Email</h3>
                    <p className="text-slate-300">info@themindseyestudio.com</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-orange-500 rounded-full flex items-center justify-center">
                    <Phone className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-white">Phone</h3>
                    <p className="text-slate-300">608-219-6066</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-orange-500 rounded-full flex items-center justify-center">
                    <MapPin className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-white">Location</h3>
                    <p className="text-slate-300">Based in Madison, WI but can Travel within the state</p>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
          
          {/* Contact Form - Exact match to real site */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.6 }}
          >
            <div className="bg-slate-800 rounded-lg p-8">
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="name" className="block text-sm font-medium text-white mb-2">
                      Name *
                    </label>
                    <input
                      type="text"
                      id="name"
                      name="name"
                      required
                      value={formData.name}
                      onChange={handleChange}
                      className="w-full px-4 py-3 border border-slate-600 rounded-md bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                      placeholder="Your full name"
                    />
                  </div>
                  
                  <div>
                    <label htmlFor="email" className="block text-sm font-medium text-white mb-2">
                      Email *
                    </label>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      required
                      value={formData.email}
                      onChange={handleChange}
                      className="w-full px-4 py-3 border border-slate-600 rounded-md bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                      placeholder="your@email.com"
                    />
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="phone" className="block text-sm font-medium text-white mb-2">
                      Phone
                    </label>
                    <input
                      type="tel"
                      id="phone"
                      name="phone"
                      value={formData.phone}
                      onChange={handleChange}
                      className="w-full px-4 py-3 border border-slate-600 rounded-md bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                      placeholder="Your phone number"
                    />
                  </div>
                  
                  <div>
                    <label htmlFor="eventDate" className="block text-sm font-medium text-white mb-2">
                      Event Date
                    </label>
                    <input
                      type="date"
                      id="eventDate"
                      name="eventDate"
                      value={formData.eventDate}
                      onChange={handleChange}
                      className="w-full px-4 py-3 border border-slate-600 rounded-md bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                    />
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="photographyType" className="block text-sm font-medium text-white mb-2">
                      Photography Type
                    </label>
                    <select
                      id="photographyType"
                      name="photographyType"
                      value={formData.photographyType}
                      onChange={handleChange}
                      className="w-full px-4 py-3 border border-slate-600 rounded-md bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                    >
                      <option value="">Select type</option>
                      <option value="Band Promotions">Band Promotions</option>
                      <option value="Corporate">Corporate</option>
                      <option value="Event">Event</option>
                      <option value="Landscape">Landscape</option>
                      <option value="Nature">Nature</option>
                      <option value="Portrait">Portrait</option>
                      <option value="Products">Products</option>
                      <option value="Real Estate">Real Estate</option>
                    </select>
                  </div>
                  
                  <div>
                    <label htmlFor="budgetRange" className="block text-sm font-medium text-white mb-2">
                      Budget Range
                    </label>
                    <select
                      id="budgetRange"
                      name="budgetRange"
                      value={formData.budgetRange}
                      onChange={handleChange}
                      className="w-full px-4 py-3 border border-slate-600 rounded-md bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                    >
                      <option value="">Select budget</option>
                      <option value="Under $1,000">Under $1,000</option>
                      <option value="$1,000 - $2,500">$1,000 - $2,500</option>
                      <option value="$2,500 - $5,000">$2,500 - $5,000</option>
                      <option value="$5,000 - $10,000">$5,000 - $10,000</option>
                      <option value="Over $10,000">Over $10,000</option>
                    </select>
                  </div>
                </div>
                
                <div>
                  <label htmlFor="projectDescription" className="block text-sm font-medium text-white mb-2">
                    Project Description
                  </label>
                  <textarea
                    id="projectDescription"
                    name="projectDescription"
                    rows={4}
                    value={formData.projectDescription}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border border-slate-600 rounded-md bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent resize-none"
                    placeholder="Tell us about your project..."
                  />
                </div>

                <div>
                  <label htmlFor="howDidYouHear" className="block text-sm font-medium text-white mb-2">
                    How did you hear about us?
                  </label>
                  <input
                    type="text"
                    id="howDidYouHear"
                    name="howDidYouHear"
                    value={formData.howDidYouHear}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border border-slate-600 rounded-md bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                    placeholder="Google, referral, social media, etc."
                  />
                </div>
                
                <Button 
                  type="submit"
                  className="w-full bg-orange-500 hover:bg-orange-600 text-white py-3 text-lg"
                >
                  <Send className="w-5 h-5 mr-2" />
                  Send Inquiry
                </Button>
              </form>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}

export default ContactPage


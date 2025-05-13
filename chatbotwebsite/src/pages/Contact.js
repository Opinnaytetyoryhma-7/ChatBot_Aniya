import React, { useState } from 'react'
import Computer from '../assets/Computer.webp'
import '../styles/Contact.css'
import { MenuList } from '../Help/MenuList'

function Contact() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    product: '',
    message: ''
  })

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    try {
      const response = await fetch("http://localhost:8000/ticket", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          issue_description: `User: ${formData.name}, Product: ${formData.product}, Message: ${formData.message}`,
          email: formData.email
        })
      })

      if (!response.ok) throw new Error("Something went wrong")

      const data = await response.json()
      alert(data.response || "Message sent successfully!")
      setFormData({ name: '', email: '', product: '', message: '' })  // Clear form

    } catch (err) {
      alert("Failed to send message. Try again later.")
      console.error(err)
    }
  }

  return (
    <div className='contact'>
      <div className='leftSide' style={{ backgroundImage: `url(${Computer})` }}></div>
      <div className='rightSide'>
        <h1>Contact us</h1>
        <form id='contact-form' onSubmit={handleSubmit}>
          <label htmlFor='name'>Full name</label>
          <input name='name' value={formData.name} onChange={handleChange} placeholder='Enter Full Name' type='text' required />

          <label htmlFor='email'>Email</label>
          <input name='email' value={formData.email} onChange={handleChange} placeholder='Enter email' type='email' required />

          <label htmlFor="product">In case of faulty product *</label>
          <select name='product' value={formData.product} onChange={handleChange} required>
            <option value="">Choose a Product</option>
            {MenuList.map((item, index) => (
              <option key={index} value={item.name}>{item.name}</option>
            ))}
          </select>

          <label htmlFor='message'>Message</label>
          <textarea name='message' value={formData.message} onChange={handleChange} rows="6" placeholder='Enter Message' required />

          <button type='submit'>Send Message</button>
        </form>
      </div>
    </div>
  )
}

export default Contact
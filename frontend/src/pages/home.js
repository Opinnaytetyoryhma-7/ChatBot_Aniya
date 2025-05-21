import React from 'react'
import { Link } from 'react-router-dom';
import BannerImage from '../assets/AVA004241-1900x1069.webp'
import '../styles/home.css'
import ChatWidget from '../components/ChatWidget';

export default function home() {
  return (
    <div className='home' style={{ backgroundImage: `url(${BannerImage})` }}>
        
        <div className="headerContainer" >
            <h1>Random It Company</h1>
            <p>Customer Service as AI</p>
            <Link to="/menu">
            <button>Order here</button>
            </Link>
        </div>
        <ChatWidget/>
    </div>
  )
}

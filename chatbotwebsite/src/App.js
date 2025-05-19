import Navbar from './components/Navbar';
import './App.css';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Home from './pages/home'; 
import Footer from './components/Footer';
import Menu from './pages/menu';
import About from './pages/about';
import Contact from './pages/Contact';
import { useEffect, useState } from 'react';
import ProtectedPage from './Protected';
import Login from './Login';
import Register from './pages/Register';
import { CartProvider } from './Help/CartContext';
import CartPage from './pages/CartPage';
import ReviewPage from "./pages/ReviewPage";
import AdminPage from "./pages/AdminPage"

function App() {
  const [message, setMessage] = useState('');
  
  useEffect(() => {
    fetch('http://localhost:8000/api/hello')
      .then(response => response.json())
      .then(data => setMessage(data.message))
      .catch(error => console.error('Error fetching:', error));
  }, []);

  return (
    <CartProvider>
      <div className="App">
        <Router>
          <Navbar />

          <Routes>
            <Route path='/' element={<Home />} />
            <Route path='/protected' element={<ProtectedPage />} />
            <Route path='/menu' element={<Menu />} /> 
            <Route path='/about' element={<About />} />
            <Route path='/contact' element={<Contact />} />
            <Route path='/login' element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/cart" element={<CartPage />} />
            <Route path="/review" element={<ReviewPage />} />
            <Route path="/admin" element={<AdminPage />} />
          </Routes>
          
          <Footer />
        </Router>
        
        <h1>{message}</h1> 
      </div>
    </CartProvider>
  );
}

export default App;
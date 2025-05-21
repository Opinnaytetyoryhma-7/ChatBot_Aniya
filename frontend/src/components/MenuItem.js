import React, { useContext } from 'react';
import { CartContext } from '../Help/CartContext';
import '../styles/menuItem.css'; 

function MenuItem({ image, name, price, availability }) {
  const { addToCart } = useContext(CartContext);

  return (
    <div className="menuItem">
      <div className="menuItem-image" style={{ backgroundImage: `url(${image})` }}></div>
      <h3>{name}</h3>
      <p>${price}</p>
      <p>Available: {availability}</p>
      <button onClick={() => addToCart({ name, price, image })} disabled={availability === 0}>
        {availability === 0 ? 'Out of Stock' : 'Add to Cart'}
      </button>
    </div>
  );
}

export default MenuItem;
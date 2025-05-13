import React, { createContext, useState } from 'react';

export const CartContext = createContext();

export const CartProvider = ({ children }) => {
  const [cartItems, setCartItems] = useState([]);

  const addToCart = (product) => {
  console.log('Adding to cart:', product);  // Check the product being added
  setCartItems(prev => {
    const existing = prev.find(item => item.name === product.name);
    if (existing) {
      return prev.map(item =>
        item.name === product.name
          ? { ...item, quantity: item.quantity + 1 }
          : item
      );
    }
    return [...prev, { ...product, quantity: 1 }];
  });
};

  const removeFromCart = (itemToRemove) => {
    setCartItems((prevItems) =>
      prevItems.filter(item => item.name !== itemToRemove.name)
    );
  };

  // Clear cart
  const clearCart = () => {
    setCartItems([]);
  };

  return (
    <CartContext.Provider value={{ cartItems, addToCart, removeFromCart, clearCart }}>
      {children}
    </CartContext.Provider>
  );
};
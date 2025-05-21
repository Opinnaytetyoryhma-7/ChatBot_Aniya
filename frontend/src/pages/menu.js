import React, { useEffect, useState } from 'react';
import { MenuList as StaticMenuData } from '../Help/MenuList';
import MenuItem from '../components/MenuItem';
import '../styles/menu.css';

function Menu() {
  const [mergedProducts, setMergedProducts] = useState([]);

  useEffect(() => {
    const fetchAndMergeProducts = async () => {
      try {
        const response = await fetch('http://localhost:8000/products');
        const dynamicProducts = await response.json();

        // Merge dynamic availability into static data
        const merged = StaticMenuData.map(staticItem => {
          const match = dynamicProducts.find(p => p.name === staticItem.name);
          return match
            ? { ...staticItem, availability: match.availability }
            : staticItem;
        });

        setMergedProducts(merged);
      } catch (error) {
        console.error('Failed to fetch product data:', error);
        setMergedProducts(StaticMenuData); // Fallback to static if error
      }
    };

    fetchAndMergeProducts();
  }, []);

  return (
    <div className='menu'>
      <h1 className='menuTitle'>Our Items</h1>
      <div className='menuList'>
        {mergedProducts.map((menuItem, key) => (
          <MenuItem
            key={key}
            image={menuItem.image}
            name={menuItem.name}
            price={menuItem.price}
            availability={menuItem.availability}
          />
        ))}
      </div>
    </div>
  );
}

export default Menu;
import React, { useState, useEffect } from 'react';
import Logo from '../assets/test.png';
import { Link } from 'react-router-dom';
import '../styles/Navbar.css';
import ReorderIcon from '@mui/icons-material/Reorder';
import { jwtDecode } from 'jwt-decode'; 

export default function Navbar() {
    const [openLinks, setOpenLinks] = useState(false);
    const [isAdmin, setIsAdmin] = useState(false);

    useEffect(() => {
        const token = localStorage.getItem('access_token');
        if (token) {
            try {
                const decoded = jwtDecode(token); 
                setIsAdmin(decoded.admin === true);
            } catch (error) {
                console.error("Error decoding token:", error);
                setIsAdmin(false);
            }
        } else {
            setIsAdmin(false);
        }
    }, []);

    const toggleNavbar = () => {
        setOpenLinks(!openLinks);
    }

    return (
        <div className='navbar'>
            <div className='leftSide' id={openLinks ? "open" : "close"}>
                <img src={Logo} alt="Logo" />
                <div className='hiddenLinks'>
                    <Link to="/"> Home </Link>
                    <Link to="/menu"> Menu </Link>
                    <Link to="/about"> About </Link>
                    <Link to="/contact"> Contact </Link>
                    <Link to="/Login"> Login </Link>
                    <Link to="/cart"> Cart </Link>
                    <Link to="/review"> Review </Link>
                    {isAdmin && <Link to="/admin">Admin</Link>}
                </div>
            </div>
            <div className='rightSide'>
                <Link to="/"> Home </Link>
                <Link to="/menu"> Menu </Link>
                <Link to="/about"> About </Link>
                <Link to="/contact"> Contact </Link>
                <Link to="/Login"> Login </Link>
                <Link to="/cart"> Cart </Link>
                <Link to="/review"> Review </Link>
                {isAdmin && <Link to="/admin">Admin</Link>}
                <button onClick={toggleNavbar}>
                    <ReorderIcon />
                </button>
            </div>
        </div>
    )
}
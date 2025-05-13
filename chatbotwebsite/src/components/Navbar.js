import React, {useState} from 'react'
import Logo from '../assets/test.png'
import {Link} from 'react-router-dom'
import '../styles/Navbar.css'
import ReorderIcon from '@mui/icons-material/Reorder';

export default function Navbar() {

    const [openLinks, setOpenLinks] = useState(false);

    const isAdmin = localStorage.getItem('adminSecret') === 'your_admin_secret';

    const toggleNavbar = () => {
        setOpenLinks(!openLinks);
    }

  return (
    <div className='navbar'>
      <div className='leftSide' id={openLinks ? "open" : "close"}>
        <img src={Logo} />
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
            <ReorderIcon/>
        </button>
      </div>
    </div>
  )
}

import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import logo from '../assets/logo.jpeg';

const Navbar = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(localStorage.getItem('isLoggedIn') === 'true');
    const [isMenuActive, setIsMenuActive] = useState(false);
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        const handleStorageChange = () => {
            setIsLoggedIn(localStorage.getItem('isLoggedIn') === 'true');
        };
        window.addEventListener('storage', handleStorageChange);

        // Polling as a fallback for same-tab changes if custom events aren't used
        const interval = setInterval(handleStorageChange, 1000);

        return () => {
            window.removeEventListener('storage', handleStorageChange);
            clearInterval(interval);
        };
    }, []);

    const handleLogout = (e) => {
        e.preventDefault();
        localStorage.clear();
        setIsLoggedIn(false);
        navigate('/signin');
    };

    const toggleMenu = () => {
        setIsMenuActive(!isMenuActive);
    };

    const isActive = (path) => location.pathname === path;

    return (
        <nav className="navbar">
            <Link to="/" className="logo">
                <img src={logo} alt="ExamBridge Logo" style={{ height: '85px' }} />
            </Link>
            <button className="mobile-menu-btn" onClick={toggleMenu}>
                <i className={`fa-solid ${isMenuActive ? 'fa-times' : 'fa-bars'}`}></i>
            </button>
            <ul className={`nav-links ${isMenuActive ? 'active' : ''}`}>
                <li><Link to="/" className={isActive('/') ? 'active' : ''}>Home</Link></li>
                <li><Link to="/upload" className={isActive('/upload') ? 'active' : ''}>Upload</Link></li>
                <li><Link to="/results" className={isActive('/results') ? 'active' : ''}>Results</Link></li>
                <li><Link to="/resources" className={isActive('/resources') ? 'active' : ''}>Resources</Link></li>
                <li><Link to="/dashboard" className={isActive('/dashboard') ? 'active' : ''}>Dashboard</Link></li>
                <li className="logout-item">
                    {isLoggedIn ? (
                        <a href="#" onClick={handleLogout} className="btn btn-outline logout-btn"
                            style={{ padding: '0.4rem 1rem', marginTop: '-0.4rem' }}>
                            Logout
                        </a>
                    ) : (
                        <Link to="/signin" className="btn btn-outline logout-btn"
                            style={{ padding: '0.4rem 1rem', marginTop: '-0.4rem' }}>
                            Login
                        </Link>
                    )}
                </li>
            </ul>
        </nav>
    );
};

export default Navbar;

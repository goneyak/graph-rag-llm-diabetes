import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Navigation.css';

function Navigation() {
  const location = useLocation();
  
  // Check if the current path matches the link
  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <nav className="navigation">
      <div className="nav-container">
        <div className="nav-logo">
          <Link to="/">GP AI</Link>
        </div>
        
        <div className="nav-links">
          <Link to="/" className={isActive('/') ? 'active' : ''}>
            Home
          </Link>
          <Link to="/chat" className={isActive('/chat') ? 'active' : ''}>
            Chat
          </Link>
          <Link to="/upload" className={isActive('/upload') ? 'active' : ''}>
            Upload
          </Link>
        </div>
      </div>
    </nav>
  );
}

export default Navigation;

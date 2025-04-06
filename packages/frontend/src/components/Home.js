import React from 'react';
import { Link } from 'react-router-dom';
import './Home.css';

function Home() {
  return (
    <div className="home-container">
      <div className="hero-section">
        <h1>Welcome to GP AI</h1>
        <p>A powerful graph processing and AI chat application</p>
        
        <div className="cta-buttons">
          <Link to="/chat" className="cta-button primary">
            Chat with AI
          </Link>
          <Link to="/upload" className="cta-button secondary">
            Process Graph Data
          </Link>
        </div>
      </div>
      
      <div className="features-section">
        <h2>Features</h2>
        
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">💬</div>
            <h3>AI Chat</h3>
            <p>Interact with our advanced AI assistant to get answers to your questions</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h3>Graph Processing</h3>
            <p>Upload and process graph data in JSON or CSV format</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">☁️</div>
            <h3>Cloud Storage</h3>
            <p>Securely store your data in the cloud using AWS S3</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">🔍</div>
            <h3>Graph Analysis</h3>
            <p>Analyze complex relationships in your graph data</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home;

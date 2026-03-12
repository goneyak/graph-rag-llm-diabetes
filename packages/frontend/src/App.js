import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';

// Import components
import Navigation from './components/Navigation';
import Home from './components/Home';
import Chat from './components/Chat';
import Upload from './components/Upload';

function App() {
  return (
    <Router>
      <div className="App">
        <Navigation />
        
        <main className="App-main">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/upload" element={<Upload />} />
          </Routes>
        </main>
        
        <footer className="App-footer">
          <p>Graph-RAG Diabetes &copy; 2025</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;

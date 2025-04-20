import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import './Chat.css';
import GraphDisplay from './GraphDisplay';

function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [apiEndpoint, setApiEndpoint] = useState(null);
  const messagesEndRef = useRef(null);

  // Load API endpoint from runtime config
  useEffect(() => {
    fetch('/runtime-config.json')
      .then(response => response.json())
      .then(config => {
        setApiEndpoint(config.apiEndpoint);
        console.log('API Endpoint loaded:', config.apiEndpoint);
      })
      .catch(error => {
        console.error('Error loading runtime config:', error);
        // Fallback to environment variable or default
        setApiEndpoint(process.env.REACT_APP_API_ENDPOINT || 'https://api.example.com/chat');
      });
  }, []);

  // Scroll to bottom whenever messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleInputChange = (e) => {
    setInput(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!input.trim()) return;
    
    // Add user message to chat
    const userMessage = { text: input, sender: 'user', timestamp: new Date() };
    setMessages(prevMessages => [...prevMessages, userMessage]);
    
    // Clear input
    setInput('');
    
    // Set loading state
    setIsLoading(true);
    
    try {
      // Call API Gateway endpoint
      const response = await fetch(apiEndpoint || 'https://api.example.com/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage.text }),
      });
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Add AI response to chat
      const aiMessage = { 
        text: data.message || "Sorry, I couldn't process your request.", 
        sender: 'ai', 
        timestamp: new Date(),
        graphData: data.graphData || null // Store graph data if available
      };
      
      setMessages(prevMessages => [...prevMessages, aiMessage]);
      
      // Log graph data if available for debugging
      if (data.graphData) {
        console.log('Graph data received:', data.graphData);
      }
    } catch (error) {
      console.error('Error calling chat API:', error);
      
      // Add error message to chat
      const errorMessage = { 
        text: "Sorry, there was an error processing your request. Please try again.", 
        sender: 'ai', 
        timestamp: new Date(),
        isError: true
      };
      
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Format timestamp
  const formatTime = (timestamp) => {
    return new Intl.DateTimeFormat('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    }).format(timestamp);
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>Chat with GP AI</h2>
      </div>
      
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-chat">
            <p>Send a message to start chatting with GP AI</p>
          </div>
        ) : (
          messages.map((message, index) => (
            <div 
              key={index} 
              className={`message ${message.sender} ${message.isError ? 'error' : ''}`}
            >
              <div className="message-content">
                {message.sender === 'ai' ? (
                  <ReactMarkdown>{message.text}</ReactMarkdown>
                ) : (
                  <p>{message.text}</p>
                )}
                <span className="timestamp">{formatTime(message.timestamp)}</span>
                {message.graphData && <GraphDisplay graphData={message.graphData} />}
              </div>
            </div>
          ))
        )}
        
        {isLoading && (
          <div className="message ai loading">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      <form className="chat-input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={handleInputChange}
          placeholder="Type your message here..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}

export default Chat;

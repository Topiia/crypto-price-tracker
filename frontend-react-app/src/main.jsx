// src/main.jsx (Final)

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx'; // Import the App component
import './index.css'; // Global CSS (where your :root, body styles are)

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App /> 
  </React.StrictMode>,
);
// src/App.jsx

import React from 'react';
import Dashboard from './views/Dashboard';
import './App.css'; // Import the minimal App CSS

function App() {
  return (
    <div className="app-container">
      {/* The Dashboard handles all the core logic and layout */}
      <Dashboard />
    </div>
  );
}

export default App;
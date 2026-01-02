// src/App.jsx

import React from 'react';
import Dashboard from './views/Dashboard';
import ErrorBoundary from './components/ErrorBoundary';
import './App.css'; // Import the minimal App CSS

function App() {
  return (
    <div className="app-container">
      {/* Wrap Dashboard with ErrorBoundary to catch rendering errors */}
      <ErrorBoundary>
        <Dashboard />
      </ErrorBoundary>
    </div>
  );
}

export default App;
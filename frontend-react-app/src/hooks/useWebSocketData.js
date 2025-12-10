// src/hooks/useWebSocketData.js

import { useState, useEffect } from 'react';

// --- Configuration ---
// Match these to your Python backend ports
const HTTP_API_URL = 'http://localhost:8000/api/initial_data';
const WS_API_URL = 'ws://localhost:8001';

// --- Custom Hook Definition ---
const useWebSocketData = () => {
  const [dataPoints, setDataPoints] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let ws = null;
    let isMounted = true;

    // 1. Fetch Historical Data (HTTP API)
    const fetchInitialData = async () => {
      try {
        const response = await fetch(HTTP_API_URL);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const initialData = await response.json();
        
        if (isMounted) {
            setDataPoints(initialData);
            setIsLoading(false);
        }
      } catch (e) {
        if (isMounted) {
            console.error("Error fetching initial data:", e);
            setError("Could not connect to Python HTTP API.");
            setIsLoading(false);
        }
      }
    };

    // 2. Setup WebSocket (Real-Time API)
    const setupWebSocket = () => {
        ws = new WebSocket(WS_API_URL);

        ws.onopen = () => {
            console.log("WebSocket connected to Python server.");
            // Clear any previous error once connection is successful
            if (error) setError(null); 
        };

        // 3. Process incoming messages and update state
        ws.onmessage = (event) => {
            if (!isMounted) return;

            try {
                const newDataBatch = JSON.parse(event.data);
                
                // Use functional update to safely append new data
                setDataPoints(prevData => {
                    const updatedData = [...prevData, ...newDataBatch];
                    // Optional: Limit total data size
                    return updatedData.slice(-500); 
                });
                
            } catch (e) {
                console.error("Error parsing WebSocket message:", e);
            }
        };

        ws.onerror = (e) => {
            if (isMounted) {
                console.error("WebSocket Error:", e);
                // Note: The error state here needs careful management
                // to distinguish between initial failure and runtime drop.
                // For simplicity, we'll log it.
            }
        };

        ws.onclose = () => {
            console.log("WebSocket disconnected. Attempting reconnect in 5s...");
            // Professional touch: Basic automatic reconnection logic
            if (isMounted) {
                 setTimeout(setupWebSocket, 5000); 
            }
        };
    };

    fetchInitialData();
    setupWebSocket();

    // 4. Cleanup Function
    return () => {
      isMounted = false;
      if (ws && ws.readyState === 1) { 
        ws.close();
      }
      console.log("WebSocket Hook cleaned up.");
    };
  }, []); 

  return { dataPoints, isLoading, error };
};

export default useWebSocketData;
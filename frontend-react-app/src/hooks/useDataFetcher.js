// src/hooks/useDataFetcher.js

import { useState, useEffect } from 'react';

// --- Configuration ---
// Match these to your Python backend ports
const HTTP_API_URL = 'http://localhost:8000/api/initial_data';
const WS_API_URL = 'ws://localhost:8001';

// --- Custom Hook Definition ---
const useDataFetcher = () => {
  // Store all data points received (historical + real-time)
  const [dataPoints, setDataPoints] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isWebSocketConnected, setIsWebSocketConnected] = useState(false);

  useEffect(() => {
    let ws = null; // Variable to hold the WebSocket instance
    let isMounted = true; // Cleanup flag for async operations

    // ------------------------------------
    // 1. Fetch Historical Data (HTTP API)
    // ------------------------------------
    const fetchInitialData = async () => {
      try {
        const response = await fetch(HTTP_API_URL);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const initialData = await response.json();

        // Only update state if the component is mounted
        if (isMounted) {
          setDataPoints(initialData);
          setIsLoading(false);
        }
      } catch (e) {
        if (isMounted) {
          console.error("Error fetching initial data:", e);
          setError("Could not connect to Python HTTP API.");
          setIsLoading(false); // Stop loading even if error
        }
      }
    };

    // ------------------------------------
    // 2. Setup WebSocket (Real-Time API)
    // ------------------------------------
    const setupWebSocket = () => {
      ws = new WebSocket(WS_API_URL);

      ws.onopen = () => {
        console.log("WebSocket connected to Python server.");
        if (isMounted) setIsWebSocketConnected(true);
      };

      // 3. Process incoming messages and update state
      ws.onmessage = (event) => {
        if (!isMounted) return;

        try {
          // The message is a JSON string containing a list of new data points
          const newDataBatch = JSON.parse(event.data);

          // Use the functional update to safely append new data
          setDataPoints(prevData => {
            // Combine the previous data with the new batch
            const updatedData = [...prevData, ...newDataBatch];

            // Optional: Limit the total data size to maintain performance
            // e.g., keep the last 500 points total.
            return updatedData.slice(-500);
          });

        } catch (e) {
          console.error("Error parsing WebSocket message:", e);
        }
      };

      ws.onerror = (e) => {
        if (isMounted) {
          console.error("WebSocket Error:", e);
          // Don't set hard error here to avoid blocking UI, just show disconnected
        }
      };

      ws.onclose = () => {
        console.log("WebSocket disconnected.");
        if (isMounted) setIsWebSocketConnected(false);
      };
    };

    fetchInitialData();
    setupWebSocket();

    // ------------------------------------
    // 4. Cleanup Function
    // ------------------------------------
    return () => {
      isMounted = false;
      if (ws && ws.readyState === 1) { // readyState 1 means OPEN
        ws.close();
      }
      console.log("Data Fetcher Hook cleaned up.");
    };
  }, []); // Empty dependency array means this runs only ONCE on mount

  // Return the data and status for any component to consume
  return { dataPoints, isLoading, error, isWebSocketConnected };
};

export default useDataFetcher;
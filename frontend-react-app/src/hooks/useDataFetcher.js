// src/hooks/useDataFetcher.js

import { useState, useEffect, useRef } from 'react';

// --- Configuration ---
// Match these to your Python backend ports
const HTTP_API_URL = 'http://localhost:8000/api/initial_data';
const WS_API_URL = 'ws://localhost:8001';

// Reconnection configuration
const RECONNECT_DELAYS = [1000, 2000, 4000, 8000, 16000, 30000]; // ms
const MAX_RECONNECT_DELAY = 30000; // 30 seconds max

// --- Custom Hook Definition ---
const useDataFetcher = () => {
  // Store all data points received (historical + real-time)
  const [dataPoints, setDataPoints] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isWebSocketConnected, setIsWebSocketConnected] = useState(false);

  // Refs for reconnection logic (persist across renders)
  const reconnectAttemptRef = useRef(0);
  const reconnectTimeoutRef = useRef(null);
  const wsRef = useRef(null);

  useEffect(() => {
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
      // Clear any existing reconnection timeout
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }

      wsRef.current = new WebSocket(WS_API_URL);

      wsRef.current.onopen = () => {
        console.log("WebSocket connected to Python server.");
        // Reset reconnection attempt counter on successful connection
        reconnectAttemptRef.current = 0;
        if (isMounted) setIsWebSocketConnected(true);
      };

      // 3. Process incoming messages and update state
      wsRef.current.onmessage = (event) => {
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

      wsRef.current.onerror = (e) => {
        if (isMounted) {
          console.error("WebSocket Error:", e);
          // Don't set hard error here to avoid blocking UI, just show disconnected
        }
      };

      wsRef.current.onclose = (event) => {
        console.log(`WebSocket disconnected. Code: ${event.code}, Reason: ${event.reason || 'No reason provided'}`);
        if (isMounted) {
          setIsWebSocketConnected(false);

          // Attempt to reconnect with exponential backoff
          attemptReconnect();
        }
      };
    };

    // ------------------------------------
    // 3. Reconnection Logic with Exponential Backoff
    // ------------------------------------
    const attemptReconnect = () => {
      if (!isMounted) return;

      // Calculate delay using exponential backoff
      const delayIndex = Math.min(reconnectAttemptRef.current, RECONNECT_DELAYS.length - 1);
      const delay = RECONNECT_DELAYS[delayIndex];

      console.log(`Attempting to reconnect in ${delay / 1000}s (attempt ${reconnectAttemptRef.current + 1})...`);

      reconnectTimeoutRef.current = setTimeout(() => {
        if (!isMounted) return;

        reconnectAttemptRef.current++;
        console.log(`Reconnecting to WebSocket... (attempt ${reconnectAttemptRef.current})`);
        setupWebSocket();
      }, delay);
    };

    fetchInitialData();
    setupWebSocket();

    // ------------------------------------
    // 4. Cleanup Function
    // ------------------------------------
    return () => {
      isMounted = false;

      // Clear any pending reconnection timeout
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }

      // Close WebSocket if open
      if (wsRef.current && wsRef.current.readyState === 1) { // readyState 1 means OPEN
        wsRef.current.close();
      }

      console.log("Data Fetcher Hook cleaned up.");
    };
  }, []); // Empty dependency array means this runs only ONCE on mount

  // Return the data and status for any component to consume
  return { dataPoints, isLoading, error, isWebSocketConnected };
};

export default useDataFetcher;
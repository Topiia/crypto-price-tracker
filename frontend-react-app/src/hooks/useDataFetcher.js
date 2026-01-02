// src/hooks/useDataFetcher.js

import { useState, useEffect, useRef } from 'react';

// --- Configuration ---
// Match these to your Python backend ports
const HTTP_API_URL = 'http://localhost:8000/api/initial_data';
const WS_API_URL = 'ws://localhost:8001';

// Reconnection configuration
const RECONNECT_DELAYS = [1000, 2000, 4000, 8000, 16000, 30000]; // ms
const MAX_RECONNECT_DELAY = 30000; // 30 seconds max
const MAX_RECONNECT_ATTEMPTS = 10; // Hard stop after this many failures

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
        console.log("✅ WebSocket connected to Python server.");

        // Clear any pending reconnection timers
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = null;
        }

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

          // Validate data structure before updating state
          if (!Array.isArray(newDataBatch)) {
            console.error("Invalid data format: expected array, got:", typeof newDataBatch);
            return;
          }

          // Filter and validate each data point
          const validatedData = newDataBatch.filter(point => {
            // Check if point is an object
            if (!point || typeof point !== 'object') {
              console.warn("Skipping invalid data point (not an object):", point);
              return false;
            }

            // Check for required fields
            const requiredFields = ['id', 'asset_id', 'timestamp', 'price_usd', 'volume_24h'];
            const missingFields = requiredFields.filter(field => !(field in point));

            if (missingFields.length > 0) {
              console.warn(`Skipping invalid data point (missing fields: ${missingFields.join(', ')}):`, point);
              return false;
            }

            // Validate data types
            if (typeof point.price_usd !== 'number' || isNaN(point.price_usd)) {
              console.warn("Skipping data point with invalid price_usd:", point);
              return false;
            }

            if (typeof point.volume_24h !== 'number' || isNaN(point.volume_24h)) {
              console.warn("Skipping data point with invalid volume_24h:", point);
              return false;
            }

            return true;
          });

          // Only update state if we have valid data
          if (validatedData.length === 0) {
            console.warn("No valid data points in batch, skipping update");
            return;
          }

          // Use the functional update to safely append new data
          setDataPoints(prevData => {
            // Combine the previous data with the new batch
            const updatedData = [...prevData, ...validatedData];

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

      // Check if we've exhausted aggressive retry attempts - HARD STOP
      if (reconnectAttemptRef.current >= MAX_RECONNECT_ATTEMPTS) {
        console.log(`⛔ Max reconnection attempts (${MAX_RECONNECT_ATTEMPTS}) reached. Entering suspended state.`);
        console.log('ℹ️  Reconnection will resume when tab becomes visible or network is restored.');
        if (isMounted) setIsWebSocketConnected(false);
        // DO NOT schedule any more retries - hard stop here
        return;
      }

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

    // ------------------------------------
    // 4. Event-Driven Recovery Handler
    // ------------------------------------
    const handleRecoveryTrigger = () => {
      // Only attempt recovery if we're in a disconnected state
      if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
        console.log('🔄 Recovery event detected - attempting reconnection...');

        // Reset retry counter for fresh reconnection cycle
        reconnectAttemptRef.current = 0;

        // Clear any pending timers
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = null;
        }

        // Attempt connection
        setupWebSocket();
      }
    };

    fetchInitialData();
    setupWebSocket();

    // ------------------------------------
    // 5. Attach Event-Driven Recovery Listeners
    // ------------------------------------
    document.addEventListener('visibilitychange', handleRecoveryTrigger);
    window.addEventListener('online', handleRecoveryTrigger);

    // ------------------------------------
    // 6. Cleanup Function
    // ------------------------------------
    return () => {
      isMounted = false;

      // Remove event listeners
      document.removeEventListener('visibilitychange', handleRecoveryTrigger);
      window.removeEventListener('online', handleRecoveryTrigger);

      // Clear reconnection timeout
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
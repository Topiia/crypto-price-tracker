// src/hooks/useDataFetcher.js

import { useState, useEffect, useRef } from 'react';

// --- Configuration ---
const HTTP_API_URL = 'http://localhost:8000/api/initial_data';
const WS_API_URL = 'ws://localhost:8001';

// Reconnection configuration
const RECONNECT_DELAYS = [1000, 2000, 4000, 8000, 16000, 30000];
const MAX_RECONNECT_ATTEMPTS = 10;

const useDataFetcher = () => {
  const [dataPoints, setDataPoints] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isWebSocketConnected, setIsWebSocketConnected] = useState(false);

  const reconnectAttemptRef = useRef(0);

  useEffect(() => {
    const effectId = Math.random().toString(36).slice(2, 7);
    console.log(`🟡 [Effect ${effectId}] MOUNT`);

    let isMounted = true;
    let ws = null;
    let reconnectTimeout = null;

    // ------------------------------------
    // 1. Fetch Historical Data
    // ------------------------------------
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
          console.error(`[Effect ${effectId}] HTTP ERROR`, e);
          setError("Could not connect to Python HTTP API.");
          setIsLoading(false);
        }
      }
    };

    // ------------------------------------
    // 2. Setup WebSocket (Effect-owned)
    // ------------------------------------
    const setupWebSocket = () => {
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
        reconnectTimeout = null;
      }

      ws = new WebSocket(WS_API_URL);
      console.log(`🟢 [Effect ${effectId}] WS CREATED`);

      ws.onopen = () => {
        console.log(`✅ [Effect ${effectId}] WS OPEN`);
        reconnectAttemptRef.current = 0;
        if (isMounted) setIsWebSocketConnected(true);
      };

      ws.onmessage = (event) => {
        if (!isMounted) return;

        try {
          const newDataBatch = JSON.parse(event.data);
          if (!Array.isArray(newDataBatch)) return;

          setDataPoints(prev =>
            [...prev, ...newDataBatch].slice(-500)
          );
        } catch (e) {
          console.error(`[Effect ${effectId}] WS PARSE ERROR`, e);
        }
      };

      ws.onerror = (e) => {
        console.error(`❌ [Effect ${effectId}] WS ERROR`, e);
      };

      ws.onclose = (event) => {
        console.log(`🔴 [Effect ${effectId}] WS CLOSED (code=${event.code})`);
        if (isMounted) {
          setIsWebSocketConnected(false);
          attemptReconnect();
        }
      };
    };

    // ------------------------------------
    // 3. Reconnection Logic
    // ------------------------------------
    const attemptReconnect = () => {
      if (!isMounted) return;

      if (reconnectAttemptRef.current >= MAX_RECONNECT_ATTEMPTS) {
        console.log(`⛔ [Effect ${effectId}] MAX RECONNECT ATTEMPTS`);
        return;
      }

      const delayIndex = Math.min(
        reconnectAttemptRef.current,
        RECONNECT_DELAYS.length - 1
      );
      const delay = RECONNECT_DELAYS[delayIndex];

      reconnectTimeout = setTimeout(() => {
        if (!isMounted) return;

        reconnectAttemptRef.current++;
        console.log(`🔁 [Effect ${effectId}] RECONNECT ATTEMPT ${reconnectAttemptRef.current}`);
        setupWebSocket();
      }, delay);
    };

    // ------------------------------------
    // 4. Recovery Events
    // ------------------------------------
    const handleRecoveryTrigger = () => {
      if (!ws || ws.readyState !== WebSocket.OPEN) {
        console.log(`🔄 [Effect ${effectId}] RECOVERY TRIGGER`);
        reconnectAttemptRef.current = 0;

        if (reconnectTimeout) {
          clearTimeout(reconnectTimeout);
          reconnectTimeout = null;
        }

        setupWebSocket();
      }
    };

    fetchInitialData();
    setupWebSocket();

    document.addEventListener('visibilitychange', handleRecoveryTrigger);
    window.addEventListener('online', handleRecoveryTrigger);

    // ------------------------------------
    // 5. Cleanup (PROOF POINT)
    // ------------------------------------
    return () => {
      console.log(`🧹 [Effect ${effectId}] CLEANUP`);
      isMounted = false;

      document.removeEventListener('visibilitychange', handleRecoveryTrigger);
      window.removeEventListener('online', handleRecoveryTrigger);

      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
        reconnectTimeout = null;
      }

      if (ws) {
        ws.close();
        console.log(`🧹 [Effect ${effectId}] WS CLOSED BY CLEANUP`);
      }
    };
  }, []);

  return { dataPoints, isLoading, error, isWebSocketConnected };
};

export default useDataFetcher;

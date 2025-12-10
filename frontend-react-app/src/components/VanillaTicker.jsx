// src/components/VanillaTicker.jsx

import React, { useEffect, useRef, useMemo } from 'react';
import './VanillaTicker.css'; 

const VanillaTicker = ({ data }) => {
    // 1. Create a Ref to reference the DOM element directly
    const tickerRef = useRef(null);

    // 2. Performance: Get the latest price for each asset using useMemo
    const latestPrices = useMemo(() => {
        const prices = {};
        const latestPoints = {};

        // Iterate backward to find the latest point for each asset quickly
        for (let i = data.length - 1; i >= 0; i--) {
            const point = data[i];
            if (!latestPoints[point.asset_id]) {
                latestPoints[point.asset_id] = point;
            }
        }
        return latestPoints;
    }, [data]); // Recalculate only when the entire data array changes

    useEffect(() => {
        const tickerElement = tickerRef.current;
        if (!tickerElement) return;

        // 3. Pure JavaScript DOM Manipulation Logic (NO REACT/JSX)
        const updateTicker = () => {
            let tickerContent = '';
            
            // Generate the content string from the latest prices
            Object.values(latestPrices).forEach(point => {
                const change = point.price_usd - (point.price_usd * 0.999); // Mock change
                const trend = change >= 0 ? '▲' : '▼';
                const trendClass = change >= 0 ? 'up' : 'down';
                
                tickerContent += 
                    `<span class="ticker-item ${trendClass}">
                        ${point.asset_id}: $${point.price_usd.toFixed(2)} <span class="trend">${trend}</span>
                    </span>`;
            });

            // CRITICAL: Directly set the innerHTML, bypassing React's V-DOM
            tickerElement.innerHTML = tickerContent; 
        };

        // Update the ticker on mount and whenever the data dependency changes
        updateTicker();

    }, [latestPrices]); // Re-run effect when latestPrices changes

    // 4. Render a simple HTML element and attach the Ref
    return (
        <div className="vanilla-ticker-container">
            <div ref={tickerRef} className="vanilla-ticker">
                {/* Content populated by pure JS in useEffect */}
                Loading Ticker...
            </div>
        </div>
    );
};

export default VanillaTicker;
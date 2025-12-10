// src/utils/dataFormatter.js

/**
 * Formats a raw timestamp string into a readable time.
 * @param {string} isoTimestamp - The ISO 8601 timestamp string from the Python backend.
 * @returns {string} The formatted time string (e.g., "10:30:45 AM").
 */
export const formatTime = (isoTimestamp) => {
    if (!isoTimestamp) return '';
    try {
        return new Date(isoTimestamp).toLocaleTimeString();
    } catch (e) {
        console.error("Invalid timestamp format:", e);
        return 'N/A';
    }
};

/**
 * Calculates a simple rolling average for a specific metric (e.g., price).
 * @param {Array<Object>} dataPoints - The array of data points.
 * @param {number} windowSize - The size of the rolling window.
 * @param {string} metricKey - The key of the metric to average (e.g., 'price_usd').
 * @returns {number} The calculated rolling average.
 */
export const calculateRollingAverage = (dataPoints, windowSize, metricKey = 'price_usd') => {
    if (dataPoints.length === 0) return 0;

    // Get the last 'windowSize' elements
    const window = dataPoints.slice(-windowSize);

    if (window.length === 0) return 0;
    
    const sum = window.reduce((acc, point) => acc + (point[metricKey] || 0), 0);
    return sum / window.length;
};

/**
 * Formats a numeric value as a currency string.
 * @param {number} value - The numeric value.
 * @returns {string} The formatted currency string (e.g., "$60,123.45").
 */
export const formatCurrency = (value) => {
    if (typeof value !== 'number') return '$0.00';
    return `$${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 4 })}`;
};
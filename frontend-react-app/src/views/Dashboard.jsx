// src/views/Dashboard.jsx (FINAL VERSION)

import React from 'react';
import useDataFetcher from '../hooks/useDataFetcher';
import Header from '../components/Header';
import RealTimeChart from '../components/RealTimeChart';
import VanillaTicker from '../components/VanillaTicker';
import PriceTable from '../components/PriceTable'; // NEW IMPORT
import './Dashboard.css';

const Dashboard = () => {
    const { dataPoints, isLoading, error, isWebSocketConnected } = useDataFetcher();

    // Calculate unique assets from dataPoints (needed for Header and Chart)
    const uniqueAssets = Array.from(new Set(dataPoints.map(item => item.asset_id)));

    // Conditional Rendering for Loading and Errors remains the same
    if (isLoading) {
        return (
            <div className="dashboard-container center-message">
                <h1>Loading Real-Time Feed...</h1>
                <p>Establishing connections to Python APIs on ports 8000 and 8001.</p>
            </div>
        );
    }

    if (error) {
        // Error handling remains the same
        return (
            <div className="dashboard-container center-message error-message">
                <h1>Connection Error 🛑</h1>
                <p>{error}</p>
                <p>Please ensure your Python backend servers are running:</p>
                <ul>
                    <li>HTTP API: `python api_server.py` (Port 8000)</li>
                    <li>WS Server: `python websocket_server.py` (Port 8001)</li>
                </ul>
            </div>
        );
    }

    // Filter data to get only the latest price for each unique asset for the metric-area
    const latestData = uniqueAssets.map(assetId => {
        return dataPoints
            .filter(d => d.asset_id === assetId)
            .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))[0];
    }).filter(Boolean);

    // Main Content Display
    return (
        <div className="dashboard-container">
            <Header assets={uniqueAssets} isConnected={isWebSocketConnected} />

            <main className="dashboard-grid">

                {/* Panel 1: Main Chart Area (Using the RealTimeChart component) */}
                <section className="chart-area">
                    {/* Data is passed down to the chart component */}
                    <RealTimeChart data={dataPoints} uniqueAssets={uniqueAssets} />
                </section>

                {/* Panel 2: Live Metrics and Vanilla JS Ticker */}
                <aside className="metric-area">
                    <h2>Live Market Data</h2>

                    {/* Price Table Component */}
                    <PriceTable data={latestData} />
                </aside>
            </main>

            {/* Ticker Section - The Vanilla JS Beast */}
            <VanillaTicker data={dataPoints} />
        </div>
    );
};

export default Dashboard;
// src/components/RealTimeChart.jsx

import React, { useMemo, useState } from 'react';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer
} from 'recharts';
import './RealTimeChart.css';

// Component Colors (match your CSS variable)
const COLORS = {
    BTC: '#f2a900', // Bitcoin Orange
    ETH: '#627eea', // Ethereum Blue
    SOL: '#00ffbd', // Solana Green
    DOGE: '#ba9f33' // Doge Yellow
};

const RealTimeChart = ({ data, uniqueAssets }) => {
    const [selectedAsset, setSelectedAsset] = useState('BTC');

    // 3.1 Beast Feature: Data Filtering and Memoization
    // Use useMemo to filter the data only when 'data' or 'selectedAsset' changes
    const filteredData = useMemo(() => {
        // Filter the large array to show only the selected asset
        const assetData = data.filter(d => d.asset_id === selectedAsset);

        // Return only the last 100 data points for performance
        // and to keep the chart readable
        return assetData.slice(-100);
    }, [data, selectedAsset]);

    // Format the timestamp for the X-Axis tooltip
    const timeFormatter = (timestamp) => {
        return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    };

    return (
        <div className="chart-wrapper">
            <div className="chart-header">
                <h3>Price Trend: {selectedAsset}</h3>
                {/* Asset Selector (Controller for the chart) */}
                <div className="asset-selector">
                    {uniqueAssets.map(asset => (
                        <button
                            key={asset}
                            onClick={() => setSelectedAsset(asset)}
                            className={`asset-btn ${selectedAsset === asset ? 'active' : ''}`}
                            style={{ '--btn-color': COLORS[asset] || 'white' }}
                        >
                            {asset}
                        </button>
                    ))}
                </div>
            </div>

            {/* Responsive Chart Container */}
            <div className="chart-container-inner">
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                        data={filteredData}
                        margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                    >
                        <CartesianGrid strokeDasharray="3 3" stroke="#2d333b" vertical={false} />
                        <XAxis
                            dataKey="timestamp"
                            tickFormatter={timeFormatter}
                            stroke="#8b949e"
                            tick={{ fill: '#8b949e', fontSize: 12 }}
                            tickLine={false}
                            axisLine={false}
                            minTickGap={50}
                        />
                        <YAxis
                            orientation="right"
                            domain={['auto', 'auto']}
                            tickFormatter={(value) => `$${value}`}
                            stroke="#8b949e"
                            tick={{ fill: '#8b949e', fontSize: 12 }}
                            tickLine={false}
                            axisLine={false}
                            width={60}
                        />
                        <Tooltip
                            labelFormatter={(label) => timeFormatter(label)}
                            formatter={(value) => [`$${value.toFixed(2)}`, 'Price']}
                            contentStyle={{
                                backgroundColor: '#151a21',
                                border: '1px solid #2d333b',
                                borderRadius: '8px',
                                color: '#e1e1e1'
                            }}
                            itemStyle={{ color: COLORS[selectedAsset] }}
                        />

                        {/* The Line component for the selected asset */}
                        <Line
                            type="monotone"
                            dataKey="price_usd"
                            stroke={COLORS[selectedAsset]}
                            strokeWidth={2}
                            dot={false}
                            activeDot={{ r: 6, strokeWidth: 0 }}
                            isAnimationActive={false}
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default RealTimeChart;
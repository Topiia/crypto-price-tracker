// src/components/Header.jsx

import React from 'react';
import { Activity, Wifi, WifiOff } from 'lucide-react';
import './Header.css';

const Header = ({ assets, isConnected }) => {
    return (
        <header className="app-header">
            <h1 className="app-title">
                <span className="logo-icon"><Activity /></span>
                CryptoDash
            </h1>
            <nav className="asset-navigation">
                {assets && assets.length > 0 ? (
                    assets.map(asset => (
                        <span key={asset} className="nav-item">
                            {asset}
                        </span>
                    ))
                ) : (
                    <span className="nav-item loading-nav">Assets Loading...</span>
                )}
            </nav>
            <div className={`status-indicator ${isConnected ? 'online' : 'offline'}`}>
                {isConnected ? <Wifi size={16} /> : <WifiOff size={16} />}
                <span>{isConnected ? 'Live' : 'Disconnected'}</span>
            </div>
        </header>
    );
};

export default Header;
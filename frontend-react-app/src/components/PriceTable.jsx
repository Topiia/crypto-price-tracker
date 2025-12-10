import React from 'react';
import { ArrowUp, ArrowDown } from 'lucide-react';
import './PriceTable.css';

const PriceTable = ({ data }) => {
    return (
        <div className="price-table-container">
            <table className="price-table">
                <thead>
                    <tr>
                        <th>Asset</th>
                        <th>Price (USD)</th>
                        <th>Volume (24h)</th>
                        <th>Trend</th>
                    </tr>
                </thead>
                <tbody>
                    {data.map((asset) => (
                        <tr key={asset.id}>
                            <td className="asset-col">
                                <span className={`asset-badge ${asset.asset_id}`}>
                                    {asset.asset_id}
                                </span>
                            </td>
                            <td className="price-col">
                                ${asset.price_usd.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 4 })}
                            </td>
                            <td className="volume-col">
                                {asset.volume_24h.toLocaleString()}
                            </td>
                            <td className="trend-col">
                                {/* Random trend for demo since we don't have prev price readily available in this view slice */
                                    Math.random() > 0.5 ? <ArrowUp size={16} className="trend-up" /> : <ArrowDown size={16} className="trend-down" />
                                }
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default PriceTable;

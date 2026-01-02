// src/components/ErrorBoundary.jsx

import React from 'react';
import './ErrorBoundary.css';

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            hasError: false,
            error: null,
            errorInfo: null
        };
    }

    // eslint-disable-next-line no-unused-vars
    static getDerivedStateFromError(_error) {
        // Update state so the next render will show the fallback UI
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        // Log error details for debugging
        console.error('ErrorBoundary caught an error:', error, errorInfo);
        this.setState({
            error: error,
            errorInfo: errorInfo
        });
    }

    handleReset = () => {
        // Reset error state and attempt to recover
        this.setState({
            hasError: false,
            error: null,
            errorInfo: null
        });
        // Reload the page to get a fresh start
        window.location.reload();
    };

    render() {
        if (this.state.hasError) {
            return (
                <div className="error-boundary-container">
                    <div className="error-boundary-content">
                        <div className="error-icon">⚠️</div>
                        <h1>Something Went Wrong</h1>
                        <p className="error-message">
                            The application encountered an unexpected error and could not continue.
                        </p>

                        {import.meta.env.DEV && this.state.error && (
                            <details className="error-details">
                                <summary>Error Details (Development Only)</summary>
                                <pre className="error-stack">
                                    {this.state.error.toString()}
                                    {this.state.errorInfo?.componentStack}
                                </pre>
                            </details>
                        )}

                        <div className="error-actions">
                            <button onClick={this.handleReset} className="reset-button">
                                Reload Dashboard
                            </button>
                        </div>

                        <p className="error-hint">
                            If this problem persists, please check:
                        </p>
                        <ul className="error-checklist">
                            <li>Backend servers are running (ports 8000 and 8001)</li>
                            <li>Network connection is stable</li>
                            <li>Browser console for additional error messages</li>
                        </ul>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;

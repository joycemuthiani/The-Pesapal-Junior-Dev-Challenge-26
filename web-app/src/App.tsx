import React, { useState, useEffect } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import Customers from './components/Customers';
import Merchants from './components/Merchants';
import Transactions from './components/Transactions';
import QueryConsole from './components/QueryConsole';
import { api } from './services/api';
import { DatabaseStats } from './types';

type TabType = 'dashboard' | 'customers' | 'merchants' | 'transactions' | 'query';

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('dashboard');
  const [stats, setStats] = useState<DatabaseStats | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await api.getStats();
      setStats(data);
      setLoading(false);
    } catch (error) {
      console.error('Error loading stats:', error);
      setLoading(false);
    }
  };

  const refreshData = () => {
    loadStats();
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="logo-section">
            <h1>Pesapal</h1>
            <p className="subtitle">Pesapal Junior Developer Challenge &apos;26</p>
          </div>
          <div className="header-stats">
            {stats && !loading && (
              <>
                <div className="stat-badge">
                  <span className="stat-label">Customers</span>
                  <span className="stat-value">{stats.total_customers}</span>
                </div>
                <div className="stat-badge">
                  <span className="stat-label">Merchants</span>
                  <span className="stat-value">{stats.total_merchants}</span>
                </div>
                <div className="stat-badge">
                  <span className="stat-label">Transactions</span>
                  <span className="stat-value">{stats.total_transactions}</span>
                </div>
                <div className="stat-badge highlight">
                  <span className="stat-label">Total Amount</span>
                  <span className="stat-value">KES {stats.total_amount?.toFixed(2) || '0.00'}</span>
                </div>
              </>
            )}
          </div>
        </div>
      </header>

      <nav className="app-nav">
        <div className="nav-content">
          <button
            className={`nav-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            Dashboard
          </button>
          <button
            className={`nav-btn ${activeTab === 'customers' ? 'active' : ''}`}
            onClick={() => setActiveTab('customers')}
          >
            Customers
          </button>
          <button
            className={`nav-btn ${activeTab === 'merchants' ? 'active' : ''}`}
            onClick={() => setActiveTab('merchants')}
          >
            Merchants
          </button>
          <button
            className={`nav-btn ${activeTab === 'transactions' ? 'active' : ''}`}
            onClick={() => setActiveTab('transactions')}
          >
            Transactions
          </button>
          <button
            className={`nav-btn ${activeTab === 'query' ? 'active' : ''}`}
            onClick={() => setActiveTab('query')}
          >
            SQL Console
          </button>
        </div>
      </nav>

      <main className="app-main">
        {activeTab === 'dashboard' && <Dashboard stats={stats} loading={loading} onUpdate={refreshData} />}
        {activeTab === 'customers' && <Customers onUpdate={refreshData} />}
        {activeTab === 'merchants' && <Merchants onUpdate={refreshData} />}
        {activeTab === 'transactions' && <Transactions onUpdate={refreshData} />}
        {activeTab === 'query' && <QueryConsole />}
      </main>

      <footer className="app-footer">
        <p className="footer-tech">
          Python · Flask · React · TypeScript · Custom SQL Parser · B-tree Indexing
        </p>
      </footer>
    </div>
  );
}

export default App;

